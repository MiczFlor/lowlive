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

#print "Content-type: text/html\n\n";

# sys variables
$configfile = "/var/lowlive/lowlive.conf";

&read_file ($configfile);
&get_data;

#######################################################
# get list and return url

	@tracklist = &get_arrayfromfile("$vari{'basedir'}/$vari{'user'}/playlists/$vari{'file'}\.$vari{'listend'}");
	print "Content-type: $vari{'mimetype'}\n\n";
	foreach $trackurl(@tracklist) {
		chomp ($trackurl);
		$trackurl =~ s/$vari{'baseurl'}/$vari{'basedir'}/g;
		print &get_linefromfile($trackurl)."\n";
	}
	die;


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
sub get_arrayfromfile {
	open(ARRAY, $_[0]) || die $!;
		@array = <ARRAY>;
	close(ARRAY);
	return (@array);
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
sub get_linefromfile {
	open(TEMP, $_[0]) || die $!;
		my $line = <TEMP>;
	close(TEMP);
	return ($line);
}