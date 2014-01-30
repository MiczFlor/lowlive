#!/usr/bin/perl -w

# Copyright (c) 1996 Steven E. Brenner
# $Id: fup.cgi,v 1.2 1996/03/30 01:33:46 brenner Exp $

require 5.001;
require "./cgi-lib.pl";

$configfile = "/var/lowlive/lowlive.conf";
&read_file ($configfile);


########################################
# read config file

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


# end read config file
########################################

MAIN: 
{
  my (%cgi_data,  # The form data
      %cgi_cfn,   # The uploaded file(s) client-provided name(s)
      %cgi_ct,    # The uploaded file(s) content-type(s).  These are
                  #   set by the user's browser and may be unreliable
      %cgi_sfn,   # The uploaded file(s) name(s) on the server (this machine)
      $ret,       # Return value of the ReadParse call.       
      $buf        # Buffer for data read from disk.
     );

  print &PrintHeader;

  # When writing files, several options can be set..
  # Spool the files to the /tmp directory
  $cgi_lib::writefiles = "/tmp";   
 
  # Limit upload size to avoid using too much memory
  $cgi_lib::maxdata = ($vari{'maxsize'}*1000); 

  # Start off by reading and parsing the data.  Save the return value.
  # Pass references to retreive the data, the filenames, and the content-type
  $ret = &ReadParse(\%cgi_data,\%cgi_cfn,\%cgi_ct,\%cgi_sfn);

  # A bit of error checking never hurt anyone
  if (!defined $ret) {
    &unlink;
    print &HtmlTop("File Upload Results");
    &CgiDie("Error in reading and parsing of CGI input");
  } elsif (!$ret) {
    &unlink;
    print &HtmlTop("File Upload Results");
    &CgiDie("Missing parameters\n",
	    "Please use the back button on your browser to change the form.\n");
  } elsif (!defined $cgi_data{'upfile'}) {
    &unlink;
    print &HtmlTop("File Upload Results");
    &CgiDie("No file chosen\n",
	    "You have to choose a file, please use the back button of your browser.");
  } elsif (!defined $cgi_data{'title'}) {
    &unlink;
    print &HtmlTop("File Upload Results");
    &CgiDie("No title\n",
	    "You have to specify a title, please use the back button of your browser.");
  }


# getting the key for the file name
@oldkeys = split(/:/, $cgi_data{'oldkey'});

###############################################
###############################################
# SPOOLING FILE TO DISK AND WRITING INFO FILE

&check_fileending;

# move the file to the user/files/category folder
$erg= `cp $cgi_sfn{'upfile'} $vari{'basedir'}/$cgi_data{'user'}/files/$cgi_data{'category'}/$oldkeys[0]\.$fileending`;
print $erg."\n<br>";

&write_trackinfo;
&write_metafile;
&unlink;
print "<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=$vari{'maincgi'}?file=$oldkeys[0]%category=$cgi_data{'category'}%user=$cgi_data{'user'}%todo=displaytrackinfo%oldkey=$cgi_data{'oldkey'}\">\n";
print &HtmlTop("Successful Upload");
print "If the info page does not load automatically, ";
print "<a href=\"$vari{'maincgi'}?file=$oldkeys[0]%category=$cgi_data{'category'}%user=$cgi_data{'user'}%todo=displaytrackinfo%oldkey=$cgi_data{'oldkey'}\">";
print "click here</a>.";
print &HtmlBot;

###############################################
# unlink (delete) the file
sub unlink {
	unlink ($cgi_sfn{'upfile'}) or
		&CgiError("Error: Unable to delete file",
		"Error: Unable to delete file $cgi_sfn{'upfile'}: $!\n");
}

###############################################
# check for file ending
sub check_fileending {
	if ($cgi_cfn{'upfile'} =~ /\.(.*)$/) {
		($fileending) = lc($1); # change to lowercase
		print "fileending:$fileending<p>";
		if ($vari{'filetypes'} =~ /$fileending/) {
			print "fileending:$fileending OK<p>";
		} else {
			&unlink;
			print &HtmlTop("File Upload Results");
			&CgiDie("Wrong file type\n",
			"You have to specify a title, please use the back button of your browser.");
		}
	}
}

###############################################
sub write_trackinfo {
	open(INFO, ">$vari{'basedir'}/$cgi_data{'user'}/files/$cgi_data{'category'}/$oldkeys[0]\.info") || die $!;
		$vari{'info'} =~ s/\n\n/<p>/g;      #double linefeed 2 paragraph break
		$vari{'info'} =~ s/\n/<br>/g;       #single linefeed 2 line break
		print INFO "title=$cgi_data{'title'}\n";
		print INFO "author=$cgi_data{'author'}\n";
		print INFO "date=$cgi_data{'date'}\n";
		print INFO "info=$cgi_data{'info'}\n";
		print INFO "url=$cgi_data{'url'}\n";
		print INFO "link=$cgi_data{'link'}\n";
	close(INFO);
}

###############################################
sub write_metafile {
	open(META, ">$vari{'basedir'}/$cgi_data{'user'}/files/$cgi_data{'category'}/$oldkeys[0]\.$vari{'metaend'}") || die $!;
		print META "$vari{'baseurl'}/$cgi_data{'user'}/files/$cgi_data{'category'}/$oldkeys[0]\.$fileending";
	close(META);
}

  # The following lines are solely to suppress 'only used once' warnings
  $cgi_lib::writefiles = $cgi_lib::writefiles;
  $cgi_lib::maxdata    = $cgi_lib::maxdata;

}













