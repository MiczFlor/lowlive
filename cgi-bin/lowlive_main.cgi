#!/usr/bin/perl

#    @license    http://www.gnu.org/licenses/agpl.txt
#    @copyright  2000 Micz Flor
#    @link       http://www.sourcefabric.org
#    @author     Micz Flor <micz.flor@sourcefabric.org>

########################################################
# This piece of code is part of the LOWLIVE project.
# The current state is Verion 0.8.3 (15.April.2002)
#
# LOWLIVE is a multi-user system for audio storage, playlist management,
# archiving web based audio links and controlling FM transmitters from remote.
# Copyright (C)2000-2002 Micz Flor (Campware / Media Development Loan Fund)
# contact: micz@mi.cz - http://www.campware.org
# Campware encourages further development. Please let us know.
########################################################

########################################################
# get data

# print "Content-type: text/html\n\n";

# sys variables
$configfile = "/var/lowlive/lowlive.conf";
$vari{'servertime'} = `/bin/date +"%a %d.%m.%y\ %k:%M"`;
$vari{'month'} = `/bin/date +"%-m"`;	# start value, overwritten in schedule
chomp $vari{'month'};
$vari{'year'} = `/bin/date +"%Y"`;	# start value, overwritten in schedule
chomp $vari{'year'};
$vari{'day'} = `/bin/date +"%-d"`;	# start value, overwritten in schedule
chomp $vari{'day'};
@html = ();				# lines of html to be placed in template
@week = ("sun","mon","tue","wed","thu","fri","sat");
@month = ("jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec");

&read_file ($configfile);

&get_data;

# &debug; # SWITCH ON FOR DEBUGGING

(@defaultcategories) = split (/::/, $vari{'categories'});
@template = &get_arrayfromfile("$vari{'vardir'}/$vari{'template'}");

############################
# security keys
$newkey = time();
if ((length($vari{'user'}) > 0) && (-e "$vari{'vardir'}/$vari{'user'}")) {
	# read old security key from file
	@keys = split(/:/, &get_linefromfile("$vari{'vardir'}/$vari{'user'}"));
}
# end security keys
############################

###########################################################
# NEW REGISTRATION

if ($vari{'todo'} =~ /^register/ && $vari{'multiuser'} =~ /yes/) {

	if (length($vari{'user'}) < 4 || $vari{'user'} =~ s/\W//g) { # no or too short login name, also first click
		&push_title ("please fill out the registration form", $vari{'colnavtd'});
		push (@html, "<br><span class=text>Login and password need to be at least 4 letters long, and consist of alphanumerical characters only.<br>");
		&registerform;
		push (@html, "<span class=\"text\">go back to <a href=$vari{'maincgi'}>login<\/a><\/span>");
		&return_html;
	}
	elsif ($vari{'newpassword'} ne $vari{'newpassword2'} || length($vari{'newpassword'}) < 4) {
		&push_title ("please fill out the registration form", $vari{'colnavtd'});
		push (@html, "<br><span class=text>Password is either too short, or you mistyped it. Please retype.");
		&registerform;
		push (@html, "<span class=\"text\">go back to <a href=$vari{'maincgi'}>login<\/a><\/span>");
		&return_html;
	}
	elsif ($vari{'newemail'} !~ /.*\@.*\..*/) {
		&push_title ("please fill out the registration form", $vari{'colnavtd'});
		push (@html, "<br><span class=text>This does not seem to be a valid email address.");
		&registerform;
		push (@html, "<span class=\"text\">go back to <a href=$vari{'maincgi'}>login<\/a><\/span>");
		&return_html;
	}
	@users = &get_arrayfromfile("$vari{'vardir'}/$vari{'users'}");
	&find_user;
	$tempuserentry = $vari{'user'}."::".$vari{'newpassword'}."::".$vari{'newname'}."::".$vari{'newemail'}."::".$vari{'userrights'};
	if ($registered =~ /no/) {
		open(USERS,">>$vari{'vardir'}/$vari{'users'}") || die $!;
		print USERS "$tempuserentry\n";
		close (USERS);
		# make folders
        $tempbasedir = $vari{'basedir'}."/".$vari{'user'};
        mkdir $tempbasedir, 0775;
        mkdir $tempbasedir."/files", 0775;
# 		`mkdir --mode=776 $vari{'basedir'}/$vari{'user'}`;
		foreach $category(@defaultcategories) {
            mkdir $tempbasedir."/files/".$category, 0775;
		}
		# make playlists
        mkdir $tempbasedir."/playlists", 0775;
		# make scheduler
        mkdir $tempbasedir."/scheduler", 0775;
        mkdir $tempbasedir."/scheduler/daily", 0775;
        mkdir $tempbasedir."/scheduler/weekly", 0775;
        mkdir $tempbasedir."/scheduler/monthly", 0775;
        mkdir $tempbasedir."/scheduler/yearly", 0775;
        mkdir $tempbasedir."/scheduler/once", 0775;
        open(STAMP, ">$tempbasedir/scheduler/stamp") || die $!;
            print STAMP "$newstamp";
        close(STAMP);
		# set variables
		@keys = ($newkey,$newkey);
		$vari{'oldkey'} = "$newkey:$newkey";
		&get_userinfo;
		$vari{'todo'} = "displayuser";
	}
	else {
		&push_title ("please fill out the registration form", $vari{'colnavtd'});
		push (@html, "<br><span class=text>Your login name is already in use. Try another one.");
		$vari{'user'} = "";
		&registerform;
		push (@html, "go back to <a href=$vari{'maincgi'}>login<\/a>");
		&return_html;
	}
}

###########################################################
# LOGOUT

if ($vari{'todo'} =~ /logout/) {
	if (-e "$vari{'vardir'}/$vari{'user'}") {
		`rm $vari{'vardir'}/$vari{'user'}`;
	}
	$vari{'user'} = "";
	&login;
	&return_html;
}

###########################################################
# MAIL FORGOTTEN PASSWORD

if ($vari{'todo'} =~ /mailpwd/) {
	&push_title("where shall we send the password");
	if ($vari{'login'}) { # check for name
		# email?
		if ($vari{'login'} =~ /@/g) {
		}
		else { # try to match user name
		}
	}
	else { # no input found yet so display form
	}
	&return_html;
}

###########################################################
# LOGIN
if ($vari{'todo'} =~ /confirmlogin/) {
	@users = &get_arrayfromfile("$vari{'vardir'}/$vari{'users'}");
	&find_user;
	if ($temppassword ne $vari{'password'} || length($vari{'user'}) < 4 || $registered eq "no") {
		&login;
		&return_html;
	}
	else {
		@keys = ($newkey,$newkey);
		$vari{'oldkey'} = "$newkey:$newkey";
		$vari{'todo'} = "displayuser";
		&get_userinfo;
	}	
}


###########################################################
# SECURITY

# logout if no username read security key from file
@oldkeys = split(/:/, $vari{'oldkey'});
if ((length($vari{'user'}) < 1) || ($oldkeys[1] ne $keys[1])) {
	&login;
	&return_html;
}
elsif (($newkey - $oldkeys[0]) > ($vari{'timeout'}*60)) {
	&push_title("login too old, please login again", $vari{'colmisc'});
	&login;
	&return_html;
}
else {
	# write new security key to file
	$registered = "yes"; # needed for displaying navigation boxes
	$vari{'key'} = "$newkey:$keys[1]";
	&writekey2file;
	&get_userinfo;
}

# end security check
############################################################

############################
# MAIN ROUTINE

############################
# ADDING AND MANAGING FILES
if ($vari{'todo'} =~ /displaytrackinfo/) {
	&read_file("$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.info");
	$vari{'location'} = &get_linefromfile("$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.$vari{'metaend'}");
	push(@html,"<p>");
	&display_trackinfo;
	push(@html,"<\/p>");
	&push_title("your files in section \'$vari{'category'}\'");
	&display_menu4categories("user=$vari{'user'}\%todo=listfiles\%oldkey=$vari{'key'}");
	&display_filesincategory($vari{'category'});
}

############################
elsif ($vari{'todo'} =~ /edittrackinfo/) {
	&read_file("$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.info");
	$vari{'todo'} = "updatetrackinfo"; # change for the next step
	&display_trackinfoform;
}

############################
elsif ($vari{'todo'} =~ /updatetrackinfo/) {
	if ($vari{'title'} !~ /\w/ || $vari{'author'} !~ /\w/) { # rough check for location
		push (@html, "Some necessary information seems to be missing. Change that.");
		&display_trackinfoform;
	}
	else {
		&write_trackinfo;
		&display_files;
	}
}

############################
elsif ($vari{'todo'} =~ /addnewtrack/) {
	# write metafile display_addnewtrackform
	if ($vari{'location'} !~ /.*\:\/\/.*\..*\//) { # rough check for location
		&push_title ("Add a remote file to your lowlive file pool");
		push (@html, "The file location should start with some protocol - such as http:// - followed by the entire address.");
		&display_addnewtrackform;
	}
	elsif ($vari{'title'} !~ /\w/ || $vari{'author'} !~ /\w/) { # rough check for data
		&push_title ("Add a remote file to your lowlive file pool");
		push (@html, "Some necessary information seems to be missing. Change that.");
		&display_addnewtrackform;
	}
	else {
		open(META, ">$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.$vari{'metaend'}") || die $!;
			print META "$vari{'location'}";
		close(META);
		&write_trackinfo;
		&display_files;
	}
}

############################
elsif ($vari{'todo'} =~ /edittracklocation/) {
	$vari{'location'} = &get_linefromfile("$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.$vari{'metaend'}");
	&push_title("Edit track location", $vari{'colfile'});
	&display_locationform;
}

############################
elsif ($vari{'todo'} =~ /writetracklocation/) {
	if ($vari{'location'} !~ /.*\:\/\/.*\..*\//) { # rough check for location
		&push_title("Edit track location", $vari{'colfile'});
		push (@html, "The file location should start with some protocol - such as http:// - followed by the entire address.");
		&display_locationform;
	}
	else {
		open(META, ">$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.$vari{'metaend'}") || die $!;
			print META "$vari{'location'}";
		close(META);
		&display_files;
	}
}

############################
elsif ($vari{'todo'} =~ /suggesttrackdelete/) {
	&push_title("Do you want to delete the following file (yes/no)?", $vari{'colfile'});
	&read_file("$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.info");
	@info = &get_arrayfromfile("$vari{'vardir'}/$vari{'tpl_fileinfo'}");
	&merge_trackinfo;
	&replace_tplfileinfo;
	$vari{'todo'} = "deletetrack";
	push (@html, "$fileinfo<p>");
	&suggestdeleteform;
	&display_trackinfo;
}

############################
elsif ($vari{'todo'} =~ /deletetrack/) {
	if ($vari{'verify'} =~ /yes/i) {
		`rm -f $vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}*`;
	}
	&display_files;
}

############################
elsif ($vari{'todo'} =~ /categories/) {
	&push_title("Edit your categories on your lowlive server", $vari{'colfile'});
	&get_folders("$vari{'basedir'}/$vari{'user'}/files/");
	&display_categorymenu;
}

############################
elsif ($vari{'todo'} =~ /deletecategory/) {
	if ($vari{'verify'}) {
		if ($vari{'verify'} =~ /yes/i) {
			`rm -rf $vari{'basedir'}/$vari{'user'}/files/$vari{'category'}`;
		}
		&push_title("Edit your categories on your lowlive server", $vari{'colfile'});
		&get_folders("$vari{'basedir'}/$vari{'user'}/files/");
		&display_categorymenu;
	}
	else {
		&push_title("Sure you want to delete section \'$vari{'category'}\'?", $vari{'colfile'});
		push (@html, "This might effect your \(or other people\'\s) playlists...");
		&suggestdeleteform;
		&display_listfilesincategories;
	}
}

############################
elsif ($vari{'todo'} =~ /addcategory/) {
	if ($vari{'newcategory'}) {
		# check if name contains only text characters
		$tempcategory = $vari{'newcategory'};
		$vari{'newcategory'} =~ s/\W//g;
		$vari{'newcategory'} =~ s/\d//g;
		$vari{'newcategory'} = lc($vari{'newcategory'});
		if ($vari{'newcategory'} ne $tempcategory) {
			&push_title ("the name should only contain lower case characters");
			&display_formforrename;
			&return_html;
		}
		foreach $category(@categories) {
			if ($tempcategory eq $category) {
				&push_title ("the name is already used, choose another");
				&display_formforrename;
				$vari{'category'} = $tempcategory;
				&display_listfilesincategories;
				&return_html;
			}
		}
		`mkdir $vari{'basedir'}/$vari{'user'}/files/$tempcategory`;
		&push_title("Edit your categories on your lowlive server", $vari{'colfile'});
		&get_folders("$vari{'basedir'}/$vari{'user'}/files/");
		&display_categorymenu;
		`mkdir $vari{'basedir'}/$vari{'user'}/files/$tempcategory`;
	}
	else {
		&push_title("How would you like to name the new section \'$vari{'category'}\'?", $vari{'colfile'});
		&display_formforrename;
	}
}

# END ADDING AND MANAGING FILES
############################

############################
# MANAGING PLAYLISTS

elsif ($vari{'todo'} =~ /addnewlist/) {
	&push_title("Add a new playlist to your lowlive server", $vari{'collist'});
	push (@html, "Give us some more info on the new playlist:<br>");
	$vari{'todo'} = "writeplaylist";
	$vari{'file'} = $newkey;
	&playlistform;
}

############################
elsif ($vari{'todo'} =~ /writeplaylist/) {
	&write_listinfo;
	`touch $vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.$vari{'listend'}`;
	&display_lists;
}

############################
elsif ($vari{'todo'} =~ /editlistinfo/) {
	read_file("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.info");
	&push_title("Change title and information of this playlist");
	$vari{'todo'} = "writeplaylist";
	&playlistform;
}

############################
elsif ($vari{'todo'} =~ /suggestlistdelete/) {
	&push_title("Do you want to delete the following playlist (yes/no)?");
	&read_file("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.info");
	$vari{'todo'} = "deletelist";
	push (@html, "<b>$vari{'title'}<\/b><br>$vari{'info'}<p>");
	&suggestdeleteform;
}

############################
elsif ($vari{'todo'} =~ /deletelist/) {
	if ($vari{'verify'} =~ /yes/i) {
		`rm -f $vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}*`;
	}
	&display_lists;
}

############################
elsif ($vari{'todo'} =~ /moveup/) {
	@tracklist = &get_arrayfromfile("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.$vari{'listend'}");
	&read_tracklist;
	$templist = $loops[($vari{'number'}-1)];
	$loops[($vari{'number'}-1)] = $loops[$vari{'number'}];
	$loops[$vari{'number'}] = $templist;
	$templist = $meta[($vari{'number'}-1)];
	$meta[($vari{'number'}-1)] = $meta[$vari{'number'}];
	$meta[$vari{'number'}] = $templist;
	&write_playlist;
	&display4playlists;
}

############################
elsif ($vari{'todo'} =~ /movedown/) {
	@tracklist = &get_arrayfromfile("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.$vari{'listend'}");
	&read_tracklist;
	$templist = $loops[($vari{'number'}+1)];
	$loops[($vari{'number'}+1)] = $loops[$vari{'number'}];
	$loops[$vari{'number'}] = $templist;
	$templist = $meta[($vari{'number'}+1)];
	$meta[($vari{'number'}+1)] = $meta[$vari{'number'}];
	$meta[$vari{'number'}] = $templist;
	&write_playlist;
	&display4playlists;
}

############################
elsif ($vari{'todo'} =~ /remove/) {
	@tracklist = &get_arrayfromfile("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.$vari{'listend'}");
	&read_tracklist;
	splice (@meta, $vari{'number'}, 1);
	splice (@loops, $vari{'number'}, 1);
	&write_playlist;
	&display4playlists;
}

############################
elsif ($vari{'todo'} =~ /inserttrack/) {
	&read_file("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'list'}\.info");
	if ($vari{'file'}) {
		@playlist = &get_arrayfromfile("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'list'}\.$vari{'listend'}");
		$maxlist = @playlist;
		while ($maxlist > ($vari{'position'})) {
			$playlist[$maxlist] = $playlist[$maxlist-1];
			$maxlist--;
		}
		$playlist[$vari{'position'}] = "$vari{'baseurl'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.$vari{'metaend'}";

		$maxlist = @playlist;
		$counter = 1;
		open(LIST, ">$vari{'basedir'}/$vari{'user'}/playlists/$vari{'list'}\.$vari{'listend'}") || die $!;
		foreach $play(@playlist) {
			chomp($play);
			print LIST "$play\n";
		}
		close (LIST);
	}
	$vari{'todo'} = $vari{'todo'}."\%list=".$vari{'list'}."\%position=".$vari{'position'};
	push_title ("select file to include in playlist \'$vari{'title'}\'");
	push (@html, "go back to list\: \'<a href=\"$vari{'maincgi'}?user=$vari{'user'}%file=$vari{'list'}%todo=display4playlists%oldkey=$vari{'key'}\">$vari{'title'}\<\/a>'<p>");
	&display_menu4categories("user=$vari{'user'}\%todo=$vari{'todo'}\%oldkey=$vari{'key'}");
	if ($vari{'category'}) {
		push (@html, "<p><span class=\"subtitle\">section \'$vari{'category'}\' contains:<\/span><p>");
		&display_files4insert($vari{'category'}, "user=$vari{'user'}\%todo=$vari{'todo'}\%oldkey=$vari{'key'}");
	}
}

############################
elsif ($vari{'todo'} =~ /display4playlists/) {
	&display4playlists;
}

# END MANAGING PLAYLISTS
############################

############################
# SCHEDULER

elsif ($vari{'todo'} =~ /scheduler/) {
	&display_schedulerhome;
}

elsif ($vari{'todo'} =~ /killentry/) {
	push (@html, "$vari{'basedir'}\/$vari{'user'}/scheduler/$vari{'kill'}");
	`rm $vari{'basedir'}/$vari{'user'}/scheduler/$vari{'kill'}`;
	&display_schedulerhome;
}
############################
elsif ($vari{'todo'} =~ /writeschedule/) {
	($vari{'schedulemonthofyear'},$vari{'scheduledayofmonth'},$vari{'scheduleweekday'},$vari{'schedulehour'},$vari{'schedulemin'}) = split (/\:/, $vari{'schedule'});

	# adding leading "0" to day 1-9
	if (length($vari{'scheduledayofmonth'}) == 1) { $vari{'scheduledayofmonth'}="0".$vari{'scheduledayofmonth'}; }

	# writing scheduler file with file location
	if ($vari{'addfrom'} eq "files") {
		$entry = "$vari{'basedir'}\/$vari{'user'}\/files\/$vari{'category'}\/$vari{'file'}";
	}
	else {
		$entry = "$vari{'basedir'}\/$vari{'user'}\/playlists\/$vari{'file'}";
	}
#     open(my $fh, '>', "output.txt") or die $!;
	open(ENTRY,">$vari{'basedir'}\/$vari{'user'}\/scheduler\/$vari{'add'}\/$vari{'schedulemonthofyear'}$vari{'scheduledayofmonth'}$vari{'scheduleweekday'}$vari{'schedulehour'}$vari{'schedulemin'}") || die $!;
	print ENTRY "$entry";
	close (ENTRY);

	&display_schedulerhome;
}

############################
elsif ($vari{'todo'} =~ /add2schedule/) {

	&push_title ("schedule a programme");

	# if dates and times added, read variables from string
	if ($vari{'schedule'}) {
		($vari{'schedulemonthofyear'},$vari{'scheduledayofmonth'},$vari{'scheduleweekday'},$vari{'schedulehour'},$vari{'schedulemin'}) = split (/\:/, $vari{'schedule'});
	}

	# interval already added? (weekly/daily/monthly etc)
	if ($vari{'add'}) {
		&display_schedulermenu;
		&display_schedulerchoosetime;
	}
	else { # not added, choose now
		&display_schedulermenu;
		&return_html;
	}
	# check for and read details
	if ($vari{'schedule'}) {
		($vari{'schedulemonthofyear'},$vari{'scheduledayofmonth'},$vari{'scheduleweekday'},$vari{'schedulehour'},$vari{'schedulemin'}) = split (/\:/, $vari{'schedule'});
	}
	else {
		# passing the hour/min/day/week etc on to the add variable before selecting track
		$vari{'schedule'} = "$vari{'schedulemonthofyear'}\:$vari{'scheduledayofmonth'}\:$vari{'scheduleweekday'}\:$vari{'schedulehour'}\:$vari{'schedulemin'}";
	}

	# time already been posted?
	if (!($vari{'schedulemin'})) {
		&return_html; # stop here and wait for time input
	}

	# select what to add from: playlist or track?
	if (!($vari{'addfrom'})) {
		&push_title ("adding to schedule from...");
		push (@html, "<p align=center class=\"subtitle\">");
		push (@html, "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%add=$vari{'add'}\%addfrom=files\%todo=$vari{'todo'}\%schedule=$vari{'schedule'}\%oldkey=$vari{'key'}\" class=\"subtitle\">FILES<\/a>");
		push (@html, "(files and streams)");
		push (@html, " or ");
		push (@html, "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%add=$vari{'add'}\%addfrom=playlists\%todo=$vari{'todo'}\%schedule=$vari{'schedule'}\%oldkey=$vari{'key'}\" class=\"subtitle\">PLAYLISTS<\/a>");
		push (@html, "");
		push (@html, "<\/p>");
		&return_html;
	}
	else {
		# if add from file, choose category
		if ($vari{'addfrom'} eq "files" && (!$vari{'category'})) {
			&push_title ("adding to schedule from files. choose section...");
			# preparing the variables for the category menu sub routine
			&display_menu4categories("user=$vari{'user'}\%todo=$vari{'todo'}\%add=$vari{'add'}\%schedule=$vari{'schedule'}\%addfrom=$vari{'addfrom'}\%oldkey=$vari{'key'}");
			&return_html;
		}
	}

	#finally: choose what to add
	if ($vari{'addfrom'} eq "files") {
		&push_title ("adding to schedule from files in section \'$vari{'category'}\'");
		&display_menu4categories("user=$vari{'user'}\%todo=$vari{'todo'}\%add=$vari{'add'}\%schedule=$vari{'schedule'}\%addfrom=$vari{'addfrom'}\%oldkey=$vari{'key'}");
		&display_files4insert($vari{'category'}, "user=$vari{'user'}\%todo=writeschedule\%add=$vari{'add'}\%schedule=$vari{'schedule'}\%addfrom=$vari{'addfrom'}\%oldkey=$vari{'key'}");
	}
	else {
		&push_title("adding a playlist to your schedule");
		&read_playlists("$vari{'basedir'}/$vari{'user'}");
		$totalcount = @lists;
		if ($totalcount > 0) {
			push (@html, "<hr noshade size=1>");
			@lists = sort @lists;
			foreach $file(@lists) {
				push (@html, "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=writeschedule\%file=$file\%add=$vari{'add'}\%addfrom=playlists\%schedule=$vari{'schedule'}\%oldkey=$vari{'key'}\"><b>\&gt\;\&gt\;insert<\/b><\/a>:");
				&display_listinfo("$vari{'basedir'}/$vari{'user'}/playlists/$file");
			}
		}
		else {
			push (@html, "I could not find any playlists at all...");
		}
	}
}

############################
# SEARCH

elsif ($vari{'todo'} =~ /search/) {

	@matched=(); # array for matched URLs on lowlive

	&push_title("search tracks on lowlive");
	&display_searchform;
	if ($vari{'searchitem'}) { # the actual search
		@searchitems = split(/\s+/, $vari{'searchitem'});
		# search entire lowlive base
		if ($vari{'where'}  eq "lowlive") {
			@users = &get_arrayfromfile("$vari{'vardir'}/$vari{'users'}");
			foreach $user(@users) {
				$user =~ s/\:\:.*\n//g;
				if ($user ne "") {
					&search_user("$user");
				}
			}
		}
		# only locally
		else {
			&search_user($vari{'user'});
		}
		$countmatches = @matched;
		if ($countmatches == 0) {
			&push_title ("no matching entries found ...");
		}
		else  {
		@matched = sort(@matched);
			&push_title ("found the following files:");
			$counter=0;
			foreach $match(@matched) {
				if ($match =~ /$vari{'basedir'}\/(.*)\/files\/(.*)\/(.*)/) {
					&display_singlefile($match);
					push (@html, @temphtml);
					$counter=1;
				}
			}
			if ($counter == 0) {
				push (@html, "<i>no files found<\/i><br>");
			}
			&push_title ("found the following playlists:");
			$counter=0;
			foreach $match(@matched) {
				if ($match =~ /$vari{'basedir'}\/(.*)\/playlists\/(.*)/) {
					$counter=1;
					&display_listinfo($match);
				}
			}
			if ($counter == 0) {
				push (@html, "<i>no playlists found<\/i><br>");
			}
		}
	}
}


############################
# UPLOADING FILES

elsif ($vari{'todo'} =~ /uploadfiles/) {
	&display_uploadform;
}
############################
# DISPLAY VARIOUS LISTINGS

elsif ($vari{'todo'} =~ /listfiles/) {
	&display_files;
}

elsif ($vari{'todo'} =~ /listlists/) {
	&display_lists;
}

elsif ($vari{'todo'} =~ /displayuser/) {
	&display_files;
}

# END DISPLAY VARIOUS LISTINGS
############################

############################
# UPLOAD FILES

elsif ($vari{'todo'} =~ /uploadtrack/) {
	if ($vari{'userrights'} =~ /upload/) { # upload allowed
		&uploadform;
	}
	else {
		&display_sorry;
	}
}

# END UPLOAD FILES
############################

else {
	&display_sorry;
}

&return_html;

# end main routine
############################

sub display_sorry {
	push_title ("Sorry..." , $vari{'colfile'});
	push (@html, "<span class=\"text\">I could not find this feature implemented on this lowlive server.<p>");
	push (@html, "Either you do not have the rights to do what you want to, ");
	push (@html, "or the coding has not yet reached the level of maturity you desire, ");
	push (@html, "or this server decided against implementing this particular feature.<\/span>");
}

###############################################
###############################################
sub uploadform {
	&push_title ("File Upload", $vari{'colnavtd'});
	push (@html, "Uploading a file takes time; the larger the file, the longer it takes.");
	push (@html, "After starting the upload process, the interface might appear frozen for some time.");
	push (@html, "<table border=0 cellpadding=2 cellspacing=0>");
	push (@html, "<form method=POST enctype='multipart/form-data' action=$vari{'uploadcgi'}>");
	
	push (@html, "<tr><td align=right class=text>upload:\&nbsp\; <\/td>");
	push (@html, "<td colspan=3><input type=file name=upfile><\/td><\/tr>");
	push (@html, "<tr>");
	&display_categorypulldown;
	push (@html, "<td colspan=2><\/td><\/tr>");
	&display_restofform;
}


###############################################
###############################################
sub login {
	$vari{'todo'} = "confirmlogin";
	if ($vari{'multiuser'} =~ /yes/) {
		&push_title ("If you already registered, login here:", $vari{'colnavtd'});
	}
	else {
		push (@html, "Login here:");
	}
	&loginform;
	if ($vari{'multiuser'} =~ /yes/) {
		push (@html, "<span class=\"text\">If you are new to lowlive, <a href=\"$vari{'maincgi'}?todo=registernewuser\">register here<\/a><\/span><p>");
	}
# 	push (@html, "<a href=\"$vari{'maincgi'}?todo=mailpwd\">You forgot your password?<\/a>");	
}

###############################################
sub get_data {
	if ($ENV{'QUERY_STRING'} ne '') {
		$data = "$ENV{'QUERY_STRING'}";
		@data = split (/%/, $data);
		foreach $data(@data) {
			($name, $value) = split (/=/, $data);
			$vari{$name} = $value;
		}
	}
	else {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
		# Split the name-value pairs
		@pairs = split(/&/, $buffer);
		# Start list of variables in numeric order
		foreach $pair (@pairs) {
			$pair =~ tr/+/ /;
			$pair =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
			$pair =~ s/\0//g;
			$pair =~ s/<([^>]|\n)*>//g; #switch on to swallow HTML
			$pair =~ s/\r\n/\n/g;       #DOS 2 UNIX
			$pair =~ s/\r/\n/g;         #MAC 2 UNIX
			$pair =~ s/\n\n/<p>/g;      #double linefeed 2 paragraph break
			$pair =~ s/\n/<br>/g;       #single linefeed 2 spacing (easy email cut&paste)
			($name, $value) = split (/=/, $pair);
		$vari{$name} = $value;
		}
	}	
}

###############################################
sub get_userinfo {
	&get_folders("$vari{'basedir'}/$vari{'user'}/files/");
}

###############################################
sub read_file {
	open(CONF,$_[0]) || die $!;
		@conf = <CONF>;
	close(CONF);

	foreach $conf (@conf) {
		chomp $conf;
		if ($conf !~ /^\#/ && $conf !~ /^\ / && $conf ne "") { # skip lines: comments, empty and spacing in the beginning
			($name, $value) = split(/=/, $conf);
			$value =~ s/<p>/\n\n/g;      #paragraph break 2 double linefeed
			$value =~ s/<br>/\n/g;       #line break 2 single linefeed
			$vari{$name} = $value;
		}
	}
}

###############################################
sub get_date {
	@longdate = localtime($_[0]);
	$longdate = "$longdate[3]\.".++$longdate[4]."\.".($longdate[5]+1900)." $longdate[2]h:$longdate[1]m";
	return ($longdate);
}

###############################################
sub find_user {
	$registered = "no";
	foreach $user(@users) {
		if ($user =~ /(.*)::(.*)::(.*)::(.*)::(.*)/) {
			if ($vari{'user'} eq $1) {
				($temppassword, $vari{'name'}, $vari{'email'}, $vari{'rights'}) = ($2,$3,$4,$5);
				$registered = "yes";
				last;
			}
		}
	}
}

###############################################
sub writekey2file {
	umask (000);
	open(KEY,">$vari{'vardir'}/$vari{'user'}") || die $!;
	print KEY "$newkey:$keys[1]";
	close (KEY);
}

###############################################
sub push_title {
	push (@html, "<p class=\"subtitle\">");
	push (@html, uc($_[0]));
	push (@html, "<\/p>");
}

###############################################
sub return_html {
	print "Content-type: text/html\n\n";
	foreach $template(@template) {
		if ($template =~ /^<!--insert/) {
			&menu_insert;
		}
		elsif ($template =~ /^<!--files/) {
			&menu_files;
		}
		elsif ($template =~ /^<!--playlists/) {
			&menu_playlists;
		}
		elsif ($template =~ /^<!--scheduler/) {
			&menu_scheduler;
		}
		else {
			$template =~ s/baseurl/$vari{'baseurl'}/g;
			print $template;
		}
	}
	die;
}

sub menu_insert {
	print "<div align=right class=\"smalltext\">";
	if ($vari{'user'}) {
		print "$vari{'user'} \| ";
		print "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=search\%oldkey=$vari{'key'}\" class=\"smalltext\">search<\/a> \| ";	
		print "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=logout\" class=\"smalltext\">logout<\/a> \| ";
	}
	print " $vari{'place'}\ $vari{'servertime'}<\/div><br>";
	foreach $html(@html) {
		print "$html\n";
	}
}

sub menu_files {
	if ($registered eq "yes") {
print <<EOF;
	<a href="$vari{'maincgi'}?user=$vari{'user'}%todo=listfiles%oldkey=$vari{'key'}" class="menu">
	<img src="$vari{'baseurl'}/img/arrow.gif" border="0">
	list &amp; edit</a><br>
	<span class="small">all tracks on your lowlive server</span><br>
	<a href="$vari{'maincgi'}?user=$vari{'user'}%todo=addnewtrack%oldkey=$vari{'key'}" class="menu">
	<img src="$vari{'baseurl'}/img/arrow.gif" border="0">
	add from web</a><br>
	<span class="small">include remote files</span><br>
	<a href="$vari{'maincgi'}?user=$vari{'user'}%todo=uploadtrack%oldkey=$vari{'key'}" class="menu">
	<img src="$vari{'baseurl'}/img/arrow.gif" border="0">
	upload</a><br>
	<span class="small">max. size: $vari{'maxsize'}kb</span><br>
	<a href="$vari{'maincgi'}?user=$vari{'user'}%todo=categories%oldkey=$vari{'key'}" class="menu">
	<img src="$vari{'baseurl'}/img/arrow.gif" border="0">
	section\/genre</a><br>
	<span class="small">add, change, manage</span>
EOF
	}
}
sub menu_playlists {
	if ($registered eq "yes") {
print <<EOF;
	<a href="$vari{'maincgi'}?user=$vari{'user'}%todo=listlists%oldkey=$vari{'key'}" class="menu">
	<img src="$vari{'baseurl'}/img/arrow.gif" border="0">
	list &amp; edit</a><br>
	<span class="small">all lists on your lowlive server</span><br>
	<a href="$vari{'maincgi'}?user=$vari{'user'}%todo=addnewlist%oldkey=$vari{'key'}" class="menu">
	<img src="$vari{'baseurl'}/img/arrow.gif" border="0">
	new list</a><br>
	<span class="small"> add a new playlist</span>
EOF
	}
}
sub menu_scheduler {
	if ($registered eq "yes") {
print <<EOF;
	<a href="$vari{'maincgi'}?user=$vari{'user'}%todo=scheduler%oldkey=$vari{'key'}" class="menu">
	<img src="$vari{'baseurl'}/img/arrow.gif" border="0">
	schedule</a><br>
	<span class="small">control your lowlive FM from remote</span>
EOF
	}
}


###############################################
sub get_linefromfile {
	open(TEMP, $_[0]) || die $!;
		my $line = <TEMP>;
	close(TEMP);
	return ($line);
}

###############################################
sub get_arrayfromfile {
	open(ARRAY, $_[0]) || die $!;
		@array = <ARRAY>;
	close(ARRAY);
	return (@array);
}

###############################################
sub suggestdeleteform {
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	push (@html, "<input type=hidden name=oldkey value=\"$vari{'key'}\">");
	push (@html, "<input type=hidden name=todo value=\"$vari{'todo'}\">");
	push (@html, "<input type=hidden name=file value=\"$vari{'file'}\">");
	push (@html, "<input type=hidden name=user value=\"$vari{'user'}\">");
	push (@html, "<input type=hidden name=category value=\"$vari{'category'}\">");
	push (@html, "delete? ");
	push (@html, "<input type=text name=verify value=\"no\" size=3 maxlength=3>");
	push (@html, "<input type=submit>");
	push (@html, "</form>");
}

###############################################
sub loginform{
	push (@html, "<table cellpadding=2 cellspacing=0 border=0>");
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	push (@html, "<input type=hidden name=oldkey value=\"$vari{'key'}\">");
	push (@html, "<input type=hidden name=todo value=\"$vari{'todo'}\">");
	push (@html, "<tr><td class=\"text\"  align=right>login:&nbsp;<\/td><td class=\"text\"><input type=text name=user maxlength=55><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\"  align=right>password:&nbsp;<\/td><td class=\"text\" ><input type=password name=password maxlength=55><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\"  align=right><\/td><td class=\"text\">");
	push (@html, "<input type=submit><input type=reset>");
	push (@html, "<\/td><\/tr>");
	push (@html, "<\/form>");
	push (@html, "<\/table>");
}

###############################################
sub registerform{
	push (@html, "<table cellpadding=2 cellspacing=0 border=0>");
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	push (@html, "<input type=hidden name=todo value=\"$vari{'todo'}\">");
	push (@html, "<tr><td class=\"text\" align=right>full name<\/td><td class=\"text\" ><input type=text name=newname value=\"\" maxlength=55><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>login<\/td><td class=\"text\"><input type=text name=user value=\"\" maxlength=55><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>password<\/td><td class=\"text\" ><input type=password name=newpassword value=\"\" maxlength=55><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>repeat password<\/td><td class=\"text\" ><input type=password name=newpassword2 value=\"\" maxlength=55><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>email<\/td><td class=\"text\"><input type=text name=newemail value=\"\" maxlength=55><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right><\/td><td class=\"text\" >");
	push (@html, "<input type=submit><input type=reset>");
	push (@html, "<\/td><\/tr>");
	push (@html, "<\/form>");
	push (@html, "<\/table>");
}

###############################################
###############################################
# SEARCH

############################
sub display_searchform {
	push (@html, "<table cellpadding=2 cellspacing=0 border=0>");
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	push (@html, "<input type=hidden name=user value=\"$vari{'user'}\">");
	push (@html, "<input type=hidden name=todo value=\"search\">");
	push (@html, "<input type=hidden name=oldkey value=\"$vari{'key'}\">");
	push (@html, "<tr><td class=\"menu\"  align=right>search for:&nbsp;<\/td>");
	push (@html, "<td class=\"text\"><input type=text name=searchitem class=\"text\" maxlength=75 value=\"$vari{'searchitem'}\"><\/td>");
	push (@html, "<\/tr>");
	push (@html, "<tr><td>&nbsp;<\/td>");
	push (@html, "<td class=\"text\">search <input type=radio name=where value=\"local\"> local ");
	push (@html, "<input type=radio name=where value=\"lowlive\"> all files<\/td>");
	push (@html, "<\/tr>");
	push (@html, "<tr><td>&nbsp;<\/td>");
	push (@html, "<td class=\"text\">search <input type=radio name=boolean value=\"and\"> all terms ");
	push (@html, "<input type=radio name=boolean value=\"or\" selected=yes> any term<\/td>");
	push (@html, "<\/tr>");
	push (@html, "<tr><td class=\"text\" align=right><\/td><td class=\"text\">");
	push (@html, "<input type=submit><input type=reset>");
	push (@html, "<\/td><\/tr>");
	push (@html, "<\/form>");
	push (@html, "<\/table>");
}

############################
sub search_user {
	&get_folders("$vari{'basedir'}/$_[0]/files/"); # reading categories
	&read_playlists("$vari{'basedir'}/$_[0]"); # get all playlists
	&read_files("$vari{'basedir'}/$_[0]"); # get all files

	foreach $list (@lists) {
		&match_terms("$vari{'basedir'}/$_[0]/playlists/$list");
	}
	foreach $file (@files) {
		&match_terms("$vari{'basedir'}/$_[0]/files/$file");
	}
}

############################
sub match_terms {
	$matched = "";

	@info = &get_arrayfromfile("$_[0]\.info");
	foreach $info(@info) {
		$info =~ s/^\w.*\=//g; # chop the variable off the beginning
	}
	$info = join (' ', @info);
	$info =~ s/<br>//gi; # remove br tags
	$info =~ s/<p>//gi; # remove br tags

	if ($vari{'boolean'} eq "and") {
		foreach $item (@searchitems) {
			if (!($info =~ /$item/i)) {
				$matched = "no";
				last;
			}
			else {
				$matched = "yes";
			}
		}
	}
	else {
		foreach $item (@searchitems) {
			if ($info =~ /$item/i) {
				$matched = "yes";
				last;
			}
			else {
				$matched = "no";
			}
		}
	}
	if ($matched eq "yes") {
		push (@matched, $_[0]);
	}
}

###############################################
###############################################
# SUBS FOR FILE MANAGEMENT

###############################################
sub merge_trackinfo {
	foreach $info(@info) {
		$fileinfo = $fileinfo.$info;
	}
}

############################
sub display_addnewtrackform {
	push (@html, "<table cellpadding=2 cellspacing=0 border=0>");
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	push (@html, "<input type=hidden name=file value=\"$newkey\">");
	push (@html, "<tr><td class=\"text\"  align=right>track url:&nbsp;<\/td>");
	push (@html, "<td class=\"text\" ><input type=text name=location class=\"text\" maxlength=100 value=\"$vari{'location'}\">");
	push (@html, "<\/td>");
	&display_categorypulldown;
	push (@html, "<\/tr>");
	&display_restofform;
}

###############################################
sub write_trackinfo {
	open(INFO, ">$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.info") || die $!;

		$vari{'info'} =~ s/\n\n/<p>/g;      #double linefeed 2 paragraph break
		$vari{'info'} =~ s/\n/<br>/g;       #single linefeed 2 line break

		print INFO "title=$vari{'title'}\n";
		print INFO "author=$vari{'author'}\n";
		print INFO "date=$vari{'date'}\n";
		print INFO "info=$vari{'info'}\n";
		print INFO "url=$vari{'url'}\n";
		print INFO "link=$vari{'link'}\n";
	close(INFO);
}

###############################################
# ??? why did i do this ???
sub replace_tplfileinfo {
	$fileinfo =~ s/\_title/$vari{'title'}/g;
	$fileinfo =~ s/\_author/$vari{'author'}/g;
	$fileinfo =~ s/\_date/$vari{'date'}/g;
	$fileinfo =~ s/\_info/$vari{'info'}/g;
	$fileinfo =~ s/\_url/$vari{'url'}/g;
	$fileinfo =~ s/\_link/$vari{'link'}/g;
	$fileinfo =~ s/\_title/$vari{'title'}/g;
}

###############################################
sub get_folders {
	if (opendir (ITEM, $_[0])) {
		@categories=();
		while (defined ($found = readdir (ITEM))) {
			if ($found =~ /\w/g) { # anything but '.' '..' or '.name'
				$found =~ s/\..*//g;
				push (@categories, $found);
			}
		}
	}
}

###############################################
sub read_playlists {
	if (opendir (ITEM, "$_[0]/playlists")) {
		@lists=();
		while (defined ($found = readdir (ITEM))) {
			if ($found =~ /\.$vari{'listend'}$/) { # playlists
				$found =~ s/\..*//g;
				push (@lists, $found);
			}
		}
	}
}


###############################################
sub read_files {
	@files=();
	foreach $category(@categories) {
		if (opendir (ITEM, "$_[0]/files/$category")) {
			while (defined ($found = readdir (ITEM))) {
				if ($found =~ /\.info$/) { # info file
					$found =~ s/\..*//g; # chop ending
					push (@files, "$category/$found");
				}
			}
		}
	}
}

###############################################
sub display_files {
	if ($vari{'category'}) {
		push_title ("your files in section \'$vari{'category'}\'");
	}
	else {
		push_title ("choose section to list your files");
	}
	&display_menu4categories("user=$vari{'user'}\%todo=$vari{'todo'}\%oldkey=$vari{'key'}");
	if ($vari{'category'}) {
		&display_filesincategory($vari{'category'});
	}
}

###############################################
# menu for category selection
sub display_menu4categories {
	&get_folders("$vari{'basedir'}/$vari{'user'}/files/");
#	push (@html, "<span class=\"menu\">choose section<\/span><span class=\"text\">: ");

	# breaking the variable string into pairs
	@passonvar = split (/\%/, $_[0]);
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	foreach $passonvar(@passonvar) {
		($passvarname, $passvarvalue) = split (/=/, $passonvar);
		push (@html, "<input type=hidden name=\"$passvarname\" value=\"$passvarvalue\">");
	}
	push (@html, "<select name=\"category\">");
	foreach $category(@categories) {
	push (@html, "<option value=\"$category\"");
	if ($vari{'category'} eq $category) {
		push (@html, "selected");
	}
	push (@html, ">$category<\/option>");
	}
	push (@html, "<\/select>");
	push (@html, "<input type=submit>");
	push (@html, "<\/form>");
	push (@html, "<\/span><hr size=1 noshade>");
}

###############################################
sub display_filesincategory {
	$counter = 0;
	if ($_[0] ne "" && (opendir (ITEM, "$vari{'basedir'}/$vari{'user'}/files/$_[0]"))) {
	push(@html,"<span class=\"text\">");
		while (defined ($file = readdir (ITEM))) {
			if ($file =~ /\.info$/) { # info file
				$file =~ s/\..*//g;
				# pass on: file without ending, category, path without ending
				&display_singlefile("$vari{'basedir'}/$vari{'user'}/files/$_[0]/$file");
				$counter++;
				push (@html, @temphtml);
			}
		}
		if ($counter == 0) {
			push (@html, "<i>empty section<\/i>");
		}
	push(@html,"<\/span>");
	}
}

###############################################
sub display_singlefile { # pass on: file path without ending
	@temphtml = ();
	&read_file("$_[0]\.info");
	if ($_[0] =~ /$vari{'basedir'}\/(.*)\/files\/(.*)\/(.*)/) {
		($myuser, $mycategory, $myfile) = ($1, $2, $3);
		push (@temphtml, "<span class=\"textbold\">$vari{'title'}<\/span> [<i>author<\/i>: $vari{'author'} <i>section<\/i>: $mycategory]<br>");
		&get_date($myfile);
		if ($vari{'user'} ne $myuser) {
			push (@temphtml, "[<i> user: $myuser <\/i>]");
			push (@temphtml, "[<a href=\"$vari{'playtrackcgi'}?file=$myfile\%category=$mycategory\%user=$myuser\">listen<\/a>\]");
# $vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.$vari{'metaend'}
		}
		else {
			push (@temphtml, "[<a href=\"$vari{'maincgi'}?file=$myfile\%category=$mycategory\%user=$vari{'user'}\%todo=displaytrackinfo\%oldkey=$vari{'key'}\">info<\/a>]");
			push (@temphtml, "[<a href=\"$vari{'maincgi'}?file=$myfile\%category=$mycategory\%user=$vari{'user'}\%todo=edittrackinfo\%oldkey=$vari{'key'}\">edit<\/a>]");
			push (@temphtml, "[<a href=\"$vari{'maincgi'}?file=$myfile\%category=$mycategory\%user=$vari{'user'}\%todo=suggesttrackdelete\%oldkey=$vari{'key'}\">delete<\/a>\]");
			push (@temphtml, "[<a href=\"$vari{'playtrackcgi'}?file=$myfile\%category=$mycategory\%user=$myuser\">listen<\/a>\]");
			# check for local media or remote file
			$metalocation = &get_linefromfile("$_[0]\.$vari{'metaend'}");
			if ($metalocation =~ /$vari{'baseurl'}\/(.*)\/.*\/(.*)\/.*\..*/) {
				($localuser, $localcategory) = ($1, $2);
				if ($vari{'user'} ne $localuser) {
					push (@temphtml, "[<i>user: ($localuser\/$localcategory)<\/i>]"); 
				}
				else {
					push (@temphtml, "[<i>local media<\/i>]");
				}
			}
			else {
				push (@temphtml, "[<a href=\"$vari{'maincgi'}?file=$myfile\%category=$mycategory\%user=$vari{'user'}\%todo=edittracklocation\%oldkey=$vari{'key'}\">edit location<\/a>]");
			}
		}
	}
	push (@temphtml, "generated: $longdate<hr noshade size=1>");
}

######################################################
sub display_formforrename {
		push (@html, "<form method=POST action=$vari{'maincgi'}>");
		push (@html, "<input type=hidden name=oldkey value=\"$vari{'key'}\">");
		push (@html, "<input type=hidden name=todo value=\"$vari{'todo'}\">");
		push (@html, "<input type=hidden name=file value=\"$vari{'file'}\">");
		push (@html, "<input type=hidden name=user value=\"$vari{'user'}\">");
		push (@html, "<input type=hidden name=category value=\"$vari{'category'}\">");
		push (@html, "new name:\&nbsp\; ");
		push (@html, "<input type=text name=newcategory value=\"$vari{'newcategory'}\" size=12 maxlength=30>");
		push (@html, "<input type=submit>");
		push (@html, "</form>");
}

######################################################
sub display_categorymenu {
	push (@html, "<table cellpadding=3 cellspacing=0 width=100% border=0>");
	push (@html, "<tr><td width=120 class=\"menu\">");
	push (@html, "<span class=\"subtitle\">SECTIONS<\/span>");
	push (@html, "<\/td><td class=\"text\" width=300>");
	push (@html, "[<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%category=$category\%todo=addcategory\%oldkey=$vari{'key'}\">new section<\/a>]\n");
	push (@html, "<\/td><\/tr>");
	foreach $category(@categories) {
		push (@html, "<tr><td width=120 class=\"menu\">");
		push (@html, uc($category));
		push (@html, "<\/td><td class=\"text\">");
		push (@html, "[<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%category=$category\%todo=deletecategory\%oldkey=$vari{'key'}\">delete<\/a>]\n");
		push (@html, "<\/td><\/tr>");
	}
	push (@html, "<\/table>");
}
###############################################
sub display_listfilesincategories {
		push (@html, "the section \'$vari{'category'}\' contains:<p>");
		$counter = 0;
		@temphtml = ();
		opendir (ITEM, "$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}");
		while (defined ($file = readdir (ITEM))) {
			if ($file =~ /\.info$/) { # info file
				$file =~ s/\..*//g;
				&read_file("$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$file\.info");
				push (@temphtml, "<span class=\"textbold\">$vari{'title'}<\/span> [<i>author<\/i>: $vari{'author'}]<br>");
				$counter++;
			}
		}
		if ($counter > 0) {
			push (@html, @temphtml);
		}
		else {
			push (@html, "<i>empty section<\/i>");
		}
}
###############################################
sub display_files4insert {
	$counter = 0;
	@temphtml = ();
	if ($_[0] ne "" && (opendir (ITEM, "$vari{'basedir'}/$vari{'user'}/files/$_[0]"))) {
		while (defined ($file = readdir (ITEM))) {
			if ($file =~ /\.info$/) { # info file
				$file =~ s/\..*//g;
				get_date($file);
				&read_file("$vari{'basedir'}/$vari{'user'}/files/$_[0]/$file\.info");
				push (@temphtml, "<span class=\"textbold\">$vari{'title'}<\/span> [<i>author<\/i>: $vari{'author'}]<br>");
				push (@temphtml, "[<a href=\"$vari{'maincgi'}?file=$file\%category=$_[0]\%$_[1]\">insert<\/a>]");
				# check for local media or remote file
				$metalocation = &get_linefromfile("$vari{'basedir'}/$vari{'user'}/files/$_[0]/$file\.$vari{'metaend'}");
				if ($metalocation =~ /$vari{'baseurl'}\/(.*)\/(.*)\/.*\..*/) {
					($localuser, $localcategory) = ($1, $2);
					if ($vari{'user'} ne $localuser) {
						push (@temphtml, "[<i>user: ($localuser\/$localcategory)<\/i>]"); 
					}
					else {
						push (@temphtml, "[<i>local media<\/i>]");
					}
				}
				push (@temphtml, "generated: $longdate<hr noshade size=1>");
				$counter++;
			}
		}
		if ($counter > 0) {
			push (@html, @temphtml);
		}
		else {
			push (@html, "<i>empty section<\/i>");
		}
	}
}

###############################################
sub display_trackinfo {
	&push_title("track details");
	push (@html, "<table cellpadding=3 cellspacing=0 border=0 width=100\%>");
	push (@html, "<tr bgcolor=\#cccccc><td class=\"text\" align=right>title:&nbsp;<\/td>\n<td class=\"textbold\">&nbsp;$vari{'title'}\<\/td>");
	push (@html, "<td class=\"text\" align=right>author:&nbsp;<\/td>\n<td class=\"textbold\">&nbsp;$vari{'author'}<\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>date:&nbsp;<\/td>\n<td class=\"textbold\">&nbsp;$vari{'date'}\<\/td>");
	push (@html, "<td class=\"text\" align=right>section:&nbsp;<\/td>\n<td class=\"textbold\">&nbsp;$vari{'category'}<\/td><\/tr>");
	push (@html, "<tr bgcolor=\#cccccc><td class=\"text\" align=right>web url:&nbsp;<\/td><td colspan=3 class=\"textbold\">");
	push (@html, "$vari{'location'}&nbsp;<\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>home page:&nbsp;<\/td><td colspan=3 class=\"textbold\">");
	push (@html, "$vari{'url'}&nbsp;<\/td><\/tr>");
	push (@html, "<tr bgcolor=\#cccccc><td class=\"text\" align=right>lowlive url:&nbsp;<\/td><td colspan=3 class=\"textbold\">");
	push (@html, "$vari{'baseurl'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.$vari{'metaend'}&nbsp;<\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>info:&nbsp;<\/td><td colspan=3 class=\"textbold\">");
	push (@html, "$vari{'info'}&nbsp;<\/td><\/tr>");
	if ($vari{'todo'} eq "displaytrackinfo") {
		push (@html, "<tr bgcolor=\#cccccc><td class=\"text\" align=right>&nbsp;<\/td><td colspan=3 class=\"text\">");
		push (@html, "[<a href=\"$vari{'maincgi'}?file=$vari{'file'}\%category=$vari{'category'}\%user=$vari{'user'}\%todo=edittrackinfo\%oldkey=$vari{'key'}\">edit<\/a>]");
		push (@html, "[<a href=\"$vari{'maincgi'}?file=$vari{'file'}\%category=$vari{'category'}\%user=$vari{'user'}\%todo=suggesttrackdelete\%oldkey=$vari{'key'}\">delete<\/a>\]");
		push (@html, "[<a href=\"$vari{'playtrackcgi'}?file=$vari{'file'}\%category=$vari{'category'}\%user=$vari{'user'}\">listen<\/a>\]");
		push (@html, "<\/td><\/tr>");
	}
	push (@html, "<\/table>");
}

###############################################
sub display_trackinfoform {
	&push_title("Read and\/or edit track information in section \'$vari{'category'}\'", $vari{'colfile'});
	push (@html, "<table cellpadding=2 cellspacing=0 border=0>");
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	push (@html, "<input type=hidden name=file value=\"$vari{'file'}\">");
	push (@html, "<input type=hidden name=category value=\"$vari{'category'}\">");
	&display_restofform;
}

###############################################
sub display_locationform {
	&read_file("$vari{'basedir'}/$vari{'user'}/files/$vari{'category'}/$vari{'file'}\.info");
	@info = &get_arrayfromfile("$vari{'vardir'}/$vari{'tpl_fileinfo'}");
	push (@html, "<span class=\"menu\">file title:<\/span> $vari{'title'}<p>");
	&merge_trackinfo;
	&replace_tplfileinfo;
	push (@html, "$fileinfo<p>");
	push (@html, "<form method=POST action=\"$vari{'maincgi'}\">");
	push (@html, "<input type=hidden name=file value=\"$vari{'file'}\">");
	push (@html, "<input type=hidden name=oldkey value=\"$vari{'key'}\">");
	push (@html, "<input type=hidden name=category value=\"$vari{'category'}\">");
	push (@html, "<input type=hidden name=todo value=\"writetracklocation\">");
	push (@html, "<input type=hidden name=user value=\"$vari{'user'}\">");
	push (@html, "location:");
	push (@html, "<input type=text maxlength=100 size=45 name=location value=\"$vari{'location'}\"><br>");
	push (@html, "<input type=submit><input type=reset>");
	push (@html, "<\/form>");
}

###############################################
sub display_categorypulldown {
	push (@html, "<td align=\"right\" class=\"text\">category:&nbsp;<\/td>");
	push (@html, "<td class=\"text\"><select name=category>@categories");
	foreach $category(@categories) {
		if ($category ne "") { # dealing with weird empty of weird origin
			push (@html, "<option value=$category>$category<\/option>\n");
		}
	}
	push (@html, "<\/select><\/td>");
}

###############################################
sub display_restofform {
	push (@html, "<input type=hidden name=todo value=\"$vari{'todo'}\">");
	push (@html, "<input type=hidden name=user value=\"$vari{'user'}\">");
	push (@html, "<input type=hidden name=oldkey value=\"$vari{'key'}\">");
	push (@html, "<tr><td class=\"text\" align=right>title:&nbsp;<\/td>\n<td class=\"text\"><input type=text name=title value=\"$vari{'title'}\" maxlength=55><\/td>");
	push (@html, "<td class=\"text\" align=right>author:&nbsp;<\/td>\n<td class=\"text\"><input type=text name=author value=\"$vari{'author'}\" maxlength=55><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>date:&nbsp;<\/td><td class=\"text\"><input type=text name=date value=\"$vari{'date'}\" maxlength=55><\/td>");
	push (@html, "<td class=\"text\" align=right>homepage:&nbsp;<\/td><td class=\"text\" ><input type=text name=url value=\"$vari{'url'}\" maxlength=100><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right>info:<\/td><td colspan=3 class=\"text\">");
	push (@html, "<textarea wrap=virtual cols=30 rows=6 name=info>$vari{'info'}<\/textarea><\/td><\/tr>");
	push (@html, "<tr><td class=\"text\" align=right><\/td><td colspan=3 class=\"text\" >");
	push (@html, "<input type=submit><input type=reset>");
	push (@html, "<\/td><\/tr>");
	push (@html, "<\/form>");
	push (@html, "<\/table>");
}

# END MANAGING FILES
###############################################
###############################################
# MANAGING PLAYLISTS

###############################################
sub write_listinfo {
	open(INFO, ">$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.info") || die $!;

		$vari{'info'} =~ s/\n/ /g;	#get rid of line and paragraph breaks

		print INFO "title=$vari{'title'}\n";
		print INFO "info=$vari{'info'}\n";
	close(INFO);
}

###############################################
sub write_playlist {
	open(NEWFILE,">$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.$vari{'listend'}") || die $!;
	$i=0;
	foreach $meta(@meta) {
		for ($counter=0;$counter<$loops[$i];$counter++) {
			print NEWFILE $meta;
		}
	$i++;
	}
	close (NEWFILE);
}

###############################################
sub playlistform {
	push (@html, "<table cellpadding=2 cellspacing=0 border=0>");
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	push (@html, "<input type=hidden name=todo value=\"$vari{'todo'}\">");
	push (@html, "<input type=hidden name=user value=\"$vari{'user'}\">");
	push (@html, "<input type=hidden name=oldkey value=\"$vari{'key'}\">");
	push (@html, "<input type=hidden name=file value=\"$vari{'file'}\">");
	push (@html, "<tr><td class=\"text\"  align=right>title:<\/td><td class=\"text\">");
	push (@html, "<input type=text name=title value=\"$vari{'title'}\" maxlength=55>");
	push (@html, "<\/td><\/tr>");
	push (@html, "<tr><td class=\"text\"  align=right>info:<\/td><td class=\"text\">");
	push (@html, "<textarea wrap=virtual cols=35 rows=6 name=info>$vari{'info'}<\/textarea><\/td><\/tr>");
	push (@html, "<\/td><\/tr>");
	push (@html, "<tr><td class=\"text\"  align=right><\/td><td class=\"text\" >");
	push (@html, "<input type=submit><input type=reset>");
	push (@html, "<\/td><\/tr>");
	push (@html, "<\/form>");
	push (@html, "<\/table>");
}

###############################################
sub display_lists {
	&push_title("List of all playlists on your lowlive server");
	&read_playlists("$vari{'basedir'}/$vari{'user'}");
	$totalcount = @lists;
	if ($totalcount > 0) {
		push (@html, "<hr noshade size=1>");
		@lists = sort @lists;
		foreach $file(@lists) {
			&display_listinfo("$vari{'basedir'}/$vari{'user'}/playlists/$file");
		}
	}
	else {
		push (@html, "I could not find any playlists at all...");
	}
}


###############################################
sub display_listinfo {
	@tracklist = &get_arrayfromfile("$_[0]\.$vari{'listend'}");
	$countmeta = @tracklist;
	&read_file("$_[0]\.info");
	if ($_[0] =~ /$vari{'basedir'}\/(.*)\/playlists\/(.*)/) {
		($myuser, $myfile) = ($1, $2);
		$longdate = (&get_date($myfile));
		push (@html, "<span class=\"textbold\">$vari{'title'}<\/span>");
		push (@html, "<br>[<i>info<\/i>: $vari{'info'}]<br>");
		if ($countmeta == 0) {
			push (@html, "[<i>empty list<\/i>]");
		}
		else {
			push (@html, "[<a href=\"$vari{'playlistcgi'}?user=$myuser\%file=$myfile\">listen<\/a>\]");
		}
		if ($vari{'user'} ne $myuser) {
			push (@html, "[<i> user: $myuser <\/i>\]");
		}
		else {
			push (@html, "[<a href=\"$vari{'maincgi'}?user=$myuser\%file=$myfile\%todo=display4playlists\%oldkey=$vari{'key'}\">edit list<\/a>\]");
			push (@html, "[<a href=\"$vari{'maincgi'}?user=$myuser\%file=$myfile\%todo=editlistinfo\%oldkey=$vari{'key'}\">edit info<\/a>\]");
			push (@html, "[<a href=\"$vari{'maincgi'}?user=$myuser\%file=$myfile\%todo=suggestlistdelete\%oldkey=$vari{'key'}\">delete<\/a>\]");
		}
		push (@html, "[generated: $longdate]");
		push (@html, "<hr noshade size=1>");
	}
}
###############################################
sub display4playlists {
	@tracklist = &get_arrayfromfile("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.$vari{'listend'}");
	&read_file("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.info");
	&read_tracklist;
	&push_title ("playlist \'$vari{'title'}\'");
	push(@html,"<p class=\"text\"><i>info:<\/i> $vari{'info'}");
	push(@html,"[<a href=\"$vari{'maincgi'}?todo=editlistinfo\%user=$vari{'user'}\%file=$vari{'file'}\%oldkey=$vari{'key'}\" class=\"text\">edit info<\/a>]");
	push(@html,"<hr noshade size=1><\/p>");
	&return_tracklist;
}

###############################################
sub read_tracklist {
	$maxtemp = @tracklist;
	@meta = ();
	@loops = ();
	$i=0;
	while ($i<$maxtemp) {
		$foundurl = $tracklist[$i];
		push (@meta, $foundurl);
		$i++;
		$counter=1;
		while ($foundurl eq $tracklist[$i]) {
			$i++;
			$counter++;
		}
		push (@loops, $counter);
	}
}

##############################################
sub return_tracklist {
	&read_file("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.info");
	$counter=0;
	$maxtracks=@meta;
	$insert = 0;
	push (@html, "<table>");
	foreach $meta(@meta) {
		if ($meta =~ /$vari{'baseurl'}\/(.*)\..*/) {
			&read_file("$vari{'basedir'}/$1\.info");
		}
		push (@html, "<tr><td colspan=2><a href=\"$vari{'maincgi'}?user=$vari{'user'}\%position=$insert\%list=$vari{'file'}\%todo=inserttrack\%oldkey=$vari{'key'}\" class=\"text\">\&gt\;\&gt\;insert track<\/a><\/td><\/tr>");
		push (@html, "<tr><td>\&nbsp;\&nbsp;<\/td><td bgcolor=\#dddddd class=\"text\">");
		push (@html, "<span class=\"menu\">$vari{'title'}<\/span> [$vari{'title'}]<br>\n");
		push (@html, "[loops\:$loops[$counter]] ");
		if ($meta =~ /$vari{'baseurl'}\/(.*)\/files\/(.*)\/(.*)\.$vari{'metaend'}/) {
			$tempuser = $1;
			$tempcategory = $2;
			$tempfile = $3;
		}
		push (@html, "[<a href=\"$vari{'playtrackcgi'}?file=$tempfile\%category=$tempcategory\%user=$tempuser\">listen<\/a>] "); #xxx
		push (@html, "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%number=$counter\%file=$vari{'file'}\%todo=remove\%oldkey=$vari{'key'}\">remove<\/a>");
		if ($counter<$maxtracks-1) {
			push (@html, "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%number=$counter\%file=$vari{'file'}\%todo=movedown\%oldkey=$vari{'key'}\">down<\/a>");
		}
		if ($counter>0) {
			push (@html, "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%number=$counter\%file=$vari{'file'}\%todo=moveup\%oldkey=$vari{'key'}\">up<\/a>");
		}
		push (@html, "<\/td><\/tr>");
		$insert = $insert + $loops[$counter];
		$counter++;
	}
	push (@html, "<tr><td colspan=2><a href=\"$vari{'maincgi'}?user=$vari{'user'}\%position=$insert\%list=$vari{'file'}\%todo=inserttrack\%oldkey=$vari{'key'}\" class=\"text\">\&gt\;\&gt\;insert track<\/a><\/td><\/tr>");
	push (@html, "<\/table>");
}

###############################################
sub display_schedulermenu {
	push (@html,"<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=scheduler\%oldkey=$vari{'key'}\" class=\"text\">today's calendar<\/a> |");
	push (@html,"edit schedule:");
	push (@html,"<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=add2schedule\%add=daily\%oldkey=$vari{'key'}\" class=\"text\">daily<\/a>");
	push (@html,"| <a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=add2schedule\%add=weekly\%oldkey=$vari{'key'}\" class=\"text\">weekly<\/a>");
	push (@html,"| <a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=add2schedule\%add=monthly\%oldkey=$vari{'key'}\" class=\"text\">monthly<\/a>");
	push (@html,"| <a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=add2schedule\%add=yearly\%oldkey=$vari{'key'}\" class=\"text\">yearly<\/a>");
#	push (@html,"| <a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=add2schedule\%add=once\%oldkey=$vari{'key'}\" class=\"text\">one off<\/a>");
	push (@html,"<hr noshade size=1>");
}

#########################################################
sub display_schedulerhome {
	&push_title ("schedule your remote fm transmitter");

	# display for adding/removing programme to schedule
	&display_schedulermenu;

	# build the three months for navigation
	&build_monthnav;

	# show today's date
	# first get weekday
	$tempweekday = `/bin/date -d "$vari{'day'} $month[$vari{'month'}-1] $vari{'year'}" +"%a"`;
	chomp ($tempweekday);
	$tempweekday = lc($tempweekday);
	&push_title ("scheduled on $tempweekday, $vari{'day'}\.$month[$vari{'month'}-1]\.$vari{'year'}");

	# get the daily schedule entries first
	&get_daily;

	# get the weekly schedules
	&get_weekly($tempweekday); # use tempweekday because that's how the scheduler saved the files

	# get the monthly schedules
	if ($vari{'day'} < 10) {
		$tempday = "0".$vari{'day'};
	}
	else {
		$tempday = $vari{'day'};
	}
	&get_monthly($tempday); # use tempday to have leading "0" in case of <10

	# get the yearly schedules
	&get_yearly($month[$vari{'month'}-1],$tempday); # use three letter name for month

	@daytime = keys(%scheduler);
	@daytime = sort(@daytime);

	push (@html, "<table width=100\% border=0 cellpadding=2 cellspacing=0>");
	push (@html, "<tr bgcolor=\#999999>");
	push (@html, "<td class=\"text\">TIME<\/td>");
	push (@html, "<td class=\"text\">TYPE<\/td>");
	push (@html, "<td class=\"text\">WHEN<\/td>");
	push (@html, "<td class=\"text\">KILL<\/td>");
	push (@html, "<td class=\"text\">INFO<\/td>");
	push (@html, "<\/tr>");
	foreach $daytime(@daytime) {
		# odd lines white, even grey
		if ($even == 1) {
			push (@html, "<tr bgcolor=\#cccccc>");
			$even = 0;
		}
		else {
			push (@html, "<tr>");
			$even = 1;
		}
			
		($when, $month, $day, $dayofweek, $file) = split (/:/, $scheduler{$daytime});
		&read_file("$file\.info");

		push (@html, "<td class=\"text\">".substr($daytime,0,2)."\:".substr($daytime,2,2)."<\/td>");
		push (@html, "<td class=\"text\">");
		if ($file =~ /$vari{'basedir'}\/$vari{'user'}\/files/) {
			push (@html, "file");
		}
		else {
			push (@html, "list");
		}
		push (@html, "<\/td>");

		push (@html, "<td class=\"text\">$when<\/td>");
		# change scheduler variables to write file into kill variable
			if ($day eq "day") { $day = ""; }
			if ($month eq "month") { $month = ""; }
			if ($dayofweek eq "dayofweek") { $dayofweek = ""; }
		$passvariables = "todo=killentry\%user=$vari{'user'}\%kill=$when\/$month$day$dayofweek$daytime\%day=$vari{'day'}\%month=$vari{'month'}\%year=$vari{'year'}\%oldkey=$vari{'key'}";
		push (@html, "<td><a href=\"$vari{'maincgi'}?$passvariables\" class=\"text\">delete<\/a><\/td>");
		$passvariables = "";
		if ($file =~ /$vari{'basedir'}\/(.*)\/files\/(.*)\/(.*)/ && $1 eq $vari{'user'}) {
			$passvariables = "todo=displaytrackinfo\%category=$2\%file=$3\%user=$1\%oldkey=$vari{'key'}";
		}
		elsif ($file =~ /$vari{'basedir'}\/(.*)\/playlists\/(.*)/ && $1 eq $vari{'user'}) {
			$passvariables = "todo=display4playlists\%file=$2\%user=$1\%oldkey=$vari{'key'}";
		}
#		print "$file <br>";
#		$passvariables = "todo=displayinfo\%category=$vari{'category'}\%file=$vari{'file'}\%user=$vari{'user'}\%oldkey=$vari{'key'}";
		push (@html, "<td class=\"text\">$vari{'title'} - $vari{'author'}");
		if ($passvariables ne "") {
			push (@html, "[<a href=\"$vari{'maincgi'}?$passvariables\" class=\"text\">info<\/a>]<\/td>");
		}
		push (@html, "<\/tr>");
	}
	push (@html, "<\/table>");
}

########################################################
sub display_schedulerchoosetime {
	# checking if time is already chosen ($vari{'schedulemin'} is defined
	if ($vari{'schedulemin'}) {
		&push_title ("$vari{'add'} programme, every\:");
	}
	else {
		&push_title ("choose time for a new $vari{'add'} programme\:");
	}
	push (@html, "<form method=POST action=$vari{'maincgi'}>");
	push (@html, "<input type=hidden name=todo value=\"add2schedule\">");
	push (@html, "<input type=hidden name=add value=\"$vari{'add'}\">");
	push (@html, "<input type=hidden name=user value=\"$vari{'user'}\">");
	push (@html, "<input type=hidden name=oldkey value=\"$vari{'key'}\">");
	# yearly programme
	if ($vari{'add'} eq "yearly") {
		# which day of the month?
		&schedule_formdayofmonth;
		# which month?
		&schedule_formmonthofyear;
		
	}
	# monthly programme
	if ($vari{'add'} eq "monthly") {
		# which day of the month?
		&schedule_formdayofmonth;
		
	}
	# weekly programme
	if ($vari{'add'} eq "weekly") {
		# which week day?
		&schedule_formweekday;	
	}
	# which hour?
	if ($vari{'schedulehour'}) {
	}
	else {
		$vari{'schedulehour'} = `/bin/date +"%k"`;
		chomp $vari{'schedulehour'};
	}
	&schedule_formhour;
	# which minute? this is different.
	# using temp variable, so that if def schedulemin means that time has been chosen
	if ($vari{'schedulemin'}) {
		$tempmin = $vari{'schedulemin'};
	}
	else {
		$tempmin = `/bin/date +"%M"`;
		chomp $tempmin;
	}
	&schedule_formmin;

	push (@html, "\&nbsp\;<input type=submit value=\"add\">");
	push (@html,"<\/form>");
}

########################################################
sub build_monthnav {
	push(@html,"<table width=100%><tr>");
	# last month
	$month=$vari{'month'}-1;
	$year=$vari{'year'};
	if ($month == 0) {
		$month = 12;
		$year--;
	}
	push (@html,"<td class=\"smalltext\" valign=top align=left>");
	if ($year > 1970) {
		&build_calhtml($month,$year);
	}
	push (@html,"<\/td>");
	# this month
	push (@html,"<td class=\"smalltext\" valign=top align=center>");
	&build_calhtml($vari{'month'},$vari{'year'});
	push (@html,"<\/td>");

	# next month
	$month=$vari{'month'}+1;
	$year=$vari{'year'};
	if ($month == 13) {
		$month = 1;
		$year++;
	}
	push (@html,"<td class=\"smalltext\" valign=top align=right>");
	&build_calhtml($month,$year);
	push (@html,"<\/td>");
	push (@html,"<\/tr><\/table>");
}

########################################################
sub schedule_formmonthofyear {
	# month already chosen? if not: use today's month
	if ($vari{'schedulemonthofyear'}) {
	}
	else {
		$vari{'schedulemonthofyear'} = `/bin/date +"%b"`;
		chomp $vari{'schedulemonthofyear'};
		$vari{'schedulemonthofyear'} = lc($vari{'schedulemonthofyear'});
	}

	push (@html,"<select name=schedulemonthofyear class=\"smalltext\">");
	foreach $month(@month) {
		if ($month eq $vari{'schedulemonthofyear'}) {
			push (@html,"<option value=$month selected>$month<\/option>");
		}
		else {
			push (@html,"<option value=$month>$month<\/option>");
		}
	}
	push (@html,"<\/select>");
}

########################################################
sub schedule_formdayofmonth {
	# day already chosen? if not: use today
	if ($vari{'scheduledayofmonth'}) {
	}
	else {
		$vari{'scheduledayofmonth'} = `/bin/date +"%-d"`;
		chomp $vari{'scheduledayofmonth'};
	}
	push (@html,"scheduledayofmonth:$vari{'scheduledayofmonth'}");
	push (@html,"each:");
	push (@html,"<select name=scheduledayofmonth class=\"smalltext\">");
	for ($i=1;$i<=31;$i++) {
		if ($i eq $vari{'scheduledayofmonth'}) {
			push (@html,"<option value=$i selected>$i<\/option>");
		}
		else {
			push (@html,"<option value=$i>$i<\/option>");
		}
	}
	push (@html,"<\/select>");
}

########################################################
sub schedule_formweekday {
	# check if a day has already been set, if not: use today
	if ($vari{'scheduleweekday'}) {
	}
	else {
		$vari{'scheduleweekday'} = `/bin/date +"%a"`;
		chomp $vari{'scheduleweekday'};
		$vari{'scheduleweekday'} = lc($vari{'scheduleweekday'});
	}

	push (@html,"each:");
	push (@html,"<select name=scheduleweekday class=\"smalltext\">");
	foreach $weekday(@week) {
		if ($weekday eq $vari{'scheduleweekday'}) {
			push (@html,"<option value=$weekday selected>$weekday<\/option>");
		}
		else {
			push (@html,"<option value=$weekday>$weekday<\/option>");
		}
	}
	push (@html,"<\/select>");
}

########################################################
sub schedule_formhour {
	push (@html,"\&nbsp;(hh:mm):");
	push (@html,"<select name=schedulehour>");
	for ($counter=0;$counter<=23;$counter++) {
		$hour=$counter;
		if ($counter < 10) {
			$hour="0".$counter;
		}	
		if ($hour eq $vari{'schedulehour'}) {
			push (@html,"<option value=$hour selected>$hour<\/option>");
		}
		else {
			push (@html,"<option value=$hour>$hour<\/option>");
		}
	}
	push (@html,"<\/select>");
}

########################################################
sub schedule_formmin {
	push (@html,"<select name=schedulemin>");
	for ($counter=0;$counter<=59;$counter++) {
		$min=$counter;
		if ($counter < 10) {
			$min="0".$counter;
		}	
		if ($min eq $tempmin) {
			push (@html,"<option value=$min selected>$min<\/option>");
		}
		else {
			push (@html,"<option value=$min>$min<\/option>");
		}
	}
	push (@html,"<\/select>");
}

########################################################
sub build_calhtml {

	# read the cal entry for the month
	@cal = `cal $_[0] $_[1]`;

	# writing month (with link for prev and next)
	if ($_[0] == $vari{'month'} && $_[1] == $vari{'year'}) {
		push(@html,shift(@cal)."<br>");
	}
	else {
		if (($_[0]+100*$_[1])<($vari{'month'}+100*$vari{'year'})) {
			push(@html,"<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=scheduler\%month=$_[0]\%year=$_[1]\%oldkey=$vari{'key'}\" class=\"smalltext\">\&lt;\&lt;<\/a> ");
			push (@html,shift(@cal)."<br>");
		}
		else {
			push(@html,shift(@cal));
			push(@html," <a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=scheduler\%month=$_[0]\%year=$_[1]\%oldkey=$vari{'key'}\" class=\"smalltext\">\&gt;\&gt;<\/a><br>");
		}
	}
	shift(@cal); # killing the line with days of the week
	push (@html, "<table border=0 cellpadding=1 cellspacing=0>");

	# writing days of week
	push (@html, "<tr bgcolor=\#999999>");
	foreach $week(@week) {
		push (@html, "<td width=12 align=right class=\"text\">");
		push (@html, substr($week,0,2));
		push (@html, "<\/td>");
	}
	push (@html, "<\/tr>");

	# build today's entry
	$temptoday = `/bin/date +"%-d%Y"`;
	chomp ($temptoday);
	$temptoday = $temptoday.$month[(`/bin/date +"%-m"`-1)];
	# work through each line
	foreach $cal(@cal) {
		push (@html, "<tr>");
		chomp($cal);
		if (length($cal)>0){
			for ($i=0;$i<20;$i=$i+3) {
				$dayindex = substr($cal,$i,2);
				$dayindex =~ s/ //g;
				push (@html, "<td align=right ");
				if ("$dayindex$_[1]$month[$_[0]-1]" eq $temptoday) {# && $_[0] == $month[(`/bin/date +"%-m"`-1)]) {
					push (@html, "bgcolor=#ffffff"); # different color for today
				}
				push (@html, ">");
				if ($dayindex ne "") {
					push (@html, "<a href=\"$vari{'maincgi'}?user=$vari{'user'}\%todo=scheduler\%day=$dayindex\%month=$_[0]\%year=$_[1]\%oldkey=$vari{'key'}\" class=\"smalltext\">");
					# today is bold
					push (@html, "$dayindex");
				}
				push (@html, "<\/a><\/td>");
			}
		}
		push (@html, "<\/tr>");
	}
	push (@html, "<\/table>");
}

########################################################
sub get_daily {
	if (opendir (ITEM, "$vari{'basedir'}/$vari{'user'}/scheduler/daily")) {
		while (defined ($found = readdir (ITEM))) {
			if ($found !~ /\./g) {
				# check if file still exists (could have been deleted in list files) !!!
				$tempfile = &get_linefromfile("$vari{'basedir'}/$vari{'user'}/scheduler/daily/$found");
				if (-e "$tempfile\.info") {
					$scheduler{$found} = "daily\:month\:day\:dayofweek\:$tempfile";
				}
			}
		}
	}
}

########################################################
sub get_weekly {
	if (opendir (ITEM, "$vari{'basedir'}/$vari{'user'}/scheduler/weekly")) {
		while (defined ($found = readdir (ITEM))) {
			if ($found !~ /\./g && $found =~ /$_[0]/g) {
				# check if file still exists (could have been deleted in list files) !!!
				$tempfile = &get_linefromfile("$vari{'basedir'}/$vari{'user'}/scheduler/weekly/$found");
				if (-e "$tempfile\.info") {
					$scheduler{substr($found,3,4)} = "weekly\:month\:day\:$_[0]\:$tempfile";
				}
			}
		}
	}
}

########################################################
sub get_monthly {
	if (opendir (ITEM, "$vari{'basedir'}/$vari{'user'}/scheduler/monthly")) {
		while (defined ($found = readdir (ITEM))) {
			if ($found !~ /\./g && $found =~ /^$_[0]/) {
				# check if file still exists (could have been deleted in list files) !!!
				$tempfile = &get_linefromfile("$vari{'basedir'}/$vari{'user'}/scheduler/monthly/$found");
				if (-e "$tempfile\.info") {
					$scheduler{substr($found,2,4)} = "monthly\:month\:$_[0]\:dayofweek\:$tempfile";
				}
			}
		}
	}
}

########################################################
sub get_yearly {
	if (opendir (ITEM, "$vari{'basedir'}/$vari{'user'}/scheduler/yearly")) {
		while (defined ($found = readdir (ITEM))) {
			if ($found !~ /\./g && $found =~ /^$_[0]$_[1]/) {
				# check if file still exists (could have been deleted in list files) !!!
				$tempfile = &get_linefromfile("$vari{'basedir'}/$vari{'user'}/scheduler/yearly/$found");
				if (-e "$tempfile\.info") {
					$scheduler{substr($found,5,4)} = "yearly\:$_[0]\:$_[1]\:dayofweek\:$tempfile";
				}
			}
		}
	}
}

############################
######### debug ############
############################

sub debug {
	print "<pre>";
	print "<font color=red>\n";
	print "ENV_QuerySrting=\"$ENV{'QUERY_STRING'}\"";
	print "$_[0]\n";
	print "todo=\"$vari{'todo'}\"\n";
	print "title=\"$vari{'title'}\"\n";
	print "category=\"$vari{'category'}\"\n";
	print "file=\"$vari{'file'}\"\n";
	print "position=\"$vari{'position'}\"\n";
	print "list=\"$vari{'list'}\"\n";
	print "url=\"$vari{'url'}\"\n";
	print "defaultcategories=\"@defaultcategories\"\n";
	print "categories=\"@categories\"\n";
	print "oldkey=\"$vari{'oldkey'}\"\n";
	print "filekey=\"$vari{'filekey'}\"\n";
	print "key=\"$vari{'key'}\"\n";
	print "<\/font><br><\/pre>\n";
}















































