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
#
# CRONTAB ENTRY SHOULD LOOK SOMETHING LIKE THIS
# 0-59 * * * * perl /home/micz/lowlive/player/trigger.pl
#
########################################################

########################################################
# get data

# sys variables
$configfile = '/var/lowlive/lowlive.conf';
$vari{'servertime'} = `/bin/date +'%a %d.%m.%y\ %k:%M'`;
$vari{'month'} = `/bin/date +'%-m'`;    # start value, overwritten in schedule
chomp $vari{'month'};
$vari{'year'} = `/bin/date +'%Y'`;  # start value, overwritten in schedule
chomp $vari{'year'};
$vari{'day'} = `/bin/date +'%-d'`;  # start value, overwritten in schedule
chomp $vari{'day'};
@html = ();             # lines of html to be placed in template
@week = ('sun','mon','tue','wed','thu','fri','sat');
@month = ('jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec');

&read_file ($configfile);
&get_data;
print 'schedule user: '.$vari{'playoutuser'}.'\n';

# get the latest time stamp of trigger activity from file
$laststamp = &get_linefromfile('$vari{'basedir'}\/$vari{'playoutuser'}\/scheduler\/stamp');

&check_schedulerentries;
print '\nlaststamp:$laststamp newstamp:$newstamp\n';

# check if different time stamp from routine. if yes, play
if ($laststamp ne $newstamp) {
    # write new time stamp
    open(STAMP, '>$vari{'basedir'}/$vari{'playoutuser'}/scheduler/stamp') || die $!;
        print STAMP '$newstamp';
    close(STAMP);
    `killall $vari{'audioplayer'}`; # kill the player first
    sleep (4); # give the soundcard some time to recover
    &trigger_player;
}

###############################################
sub read_file {
    open(CONF,$_[0]) || die $!;
        @conf = <CONF>;
    close(CONF);

    foreach $conf (@conf) {
        chomp $conf;
        if ($conf !~ /^\#/ && $conf !~ /^\ / && $conf ne '') { # skip lines: comments, empty and spacing in the beginning
            ($name, $value) = split(/=/, $conf);
            $value =~ s/<p>/\n\n/g;      #paragraph break 2 double linefeed
            $value =~ s/<br>/\n/g;       #line break 2 single linefeed
            $vari{$name} = $value;
        }
    }
}

###############################################
sub get_data {
    if ($ENV{'QUERY_STRING'} ne '') {
        $data = '$ENV{'QUERY_STRING'}';
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
            $pair =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg;
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

#########################################################
sub check_schedulerentries {
    print 'CHECKING SCHEDULER\n';
    # found entries will be delivered in
    # daily\:month\:day\:dayofweek\:$tempfile
    # firstly indicates frequency, next 3 are replaced with relevant found values
    # finally the file is attached

    # show today's date
    # first get weekday
    $tempweekday = `/bin/date +'%w'`; # using the number to make sure it's english, not sys language
    chomp ($tempweekday);
    $tempweekday = lc($week[$tempweekday]);

    $tempdaytime = `/bin/date +'%H%M'`;
    chomp ($tempdaytime);

    $tempyymmdd = `/bin/date +'%y%m%d'`;
    chomp ($tempyymmdd);

    # get the daily schedule entries first
    &get_daily;

    # get the weekly schedules
    &get_weekly($tempweekday); # use tempweekday because that's how the scheduler saved the files

    # get the monthly schedules
    if ($vari{'day'} < 10) {
        $tempday = '0'.$vari{'day'};
    }
    else {
        $tempday = $vari{'day'};
    }
    &get_monthly($tempday); # use tempday to have leading '0' in case of <10

    # get the yearly schedules
    &get_yearly($month[$vari{'month'}-1],$tempday); # use three letter name for month
    
    # now we got all we need from the db and sort the times found in the daytime array

    @daytime = keys(%scheduler);
    @daytime = sort(@daytime);

    foreach $daytime(@daytime) {
        if ($tempdaytime >= $daytime) { # determine if new or not
            ($when, $month, $day, $dayofweek, $file) = split (/:/, $scheduler{$daytime});
            $newstamp = '$tempyymmdd$daytime'; # setting the highest time for this day
        }
    }
}

########################################################
sub trigger_player {
    print 'TRIGGERING PLAYER\n';
    if ($file =~ /$vari{'basedir'}\/$vari{'playoutuser'}\/files\/.*/) { # single file
        print 'playing single file\n';
        $url = &get_linefromfile('$file\.$vari{'metaend'}');
        print 'playing file at $newstamp\n';
        print 'url: $url\n';
        print 'CALLING: $vari{'audioplayer'} $vari{'audioplayerparameters'} $url\n';
        `$vari{'audioplayer'} $vari{'audioplayerparameters'} $url`; # start player with single file
    }
    else { # playlist
        print 'playing playlist\n';
        @tracklist = &get_arrayfromfile('$file\.$vari{'listend'}');
        foreach $trackurl(@tracklist) {
            chomp ($trackurl);
            $trackurl =~ s/$vari{'baseurl'}/$vari{'basedir'}/g;
            push (@urls, &get_linefromfile($trackurl)); # get urls from metafiles
            print 'pushing into url: '.&get_linefromfile($trackurl).'\n';
        }
        # write temp playlist
        open(TEMP, '>$vari{'basedir'}/$vari{'playoutuser'}/scheduler/temp\.$vari{'listend'}') || die $!;
            foreach $url(@urls) {
                print TEMP '$url\n';
            }
        close(TEMP);
        print 'playing list at $newstamp\n';
        print 'list: $file\.$vari{'listend'}\n';
        print 'CALLING: $vari{'audioplayer'} $vari{'audioplayerparameters'} $vari{'basedir'}/$vari{'playoutuser'}/scheduler/temp\.$vari{'listend'}\n';
        `$vari{'audioplayer'} $vari{'audioplayerparameters'} $vari{'basedir'}/$vari{'playoutuser'}/scheduler/temp\.$vari{'listend'}`; # start player with list
    }
}


########################################################
sub get_daily {
    if (opendir (ITEM, '$vari{'basedir'}/$vari{'playoutuser'}/scheduler/daily')) {
        while (defined ($found = readdir (ITEM))) {
            if ($found !~ /\./g) {
                print 'found daily: $found\n';
                # check if file still exists (could have been deleted in list files) !!!
                $tempfile = &get_linefromfile('$vari{'basedir'}/$vari{'playoutuser'}/scheduler/daily/$found');
                if (-e '$tempfile\.info') {
                    $scheduler{$found} = 'daily\:month\:day\:dayofweek\:$tempfile';
                }
            }
        }
    }
}

########################################################
sub get_weekly {
    if (opendir (ITEM, '$vari{'basedir'}/$vari{'playoutuser'}/scheduler/weekly')) {
        while (defined ($found = readdir (ITEM))) {
            if ($found !~ /\./g && $found =~ /$_[0]/g) {
                print 'found weekly: $found\n';
                # check if file still exists (could have been deleted in list files) !!!
                $tempfile = &get_linefromfile('$vari{'basedir'}/$vari{'playoutuser'}/scheduler/weekly/$found');
                if (-e '$tempfile\.info') {
                    $scheduler{substr($found,3,4)} = 'weekly\:month\:day\:$_[0]\:$tempfile';
                }
            }
        }
    }
}

########################################################
sub get_monthly {
    if (opendir (ITEM, '$vari{'basedir'}/$vari{'playoutuser'}/scheduler/monthly')) {
        while (defined ($found = readdir (ITEM))) {
            if ($found !~ /\./g && $found =~ /^$_[0]/) {
                print 'found monthly: $found\n';
                # check if file still exists (could have been deleted in list files) !!!
                $tempfile = &get_linefromfile('$vari{'basedir'}/$vari{'playoutuser'}/scheduler/monthly/$found');
                if (-e '$tempfile\.info') {
                    $scheduler{substr($found,2,4)} = 'monthly\:month\:$_[0]\:dayofweek\:$tempfile';
                }
            }
        }
    }
}

########################################################
sub get_yearly {
    if (opendir (ITEM, '$vari{'basedir'}/$vari{'playoutuser'}/scheduler/yearly')) {
        while (defined ($found = readdir (ITEM))) {
            if ($found !~ /\./g && $found =~ /^$_[0]$_[1]/) {
                print 'found yearly: $found\n';
                # check if file still exists (could have been deleted in list files) !!!
                $tempfile = &get_linefromfile('$vari{'basedir'}/$vari{'playoutuser'}/scheduler/yearly/$found');
                if (-e '$tempfile\.info') {
                    $scheduler{substr($found,5,4)} = 'yearly\:$_[0]\:$_[1]\:dayofweek\:$tempfile';
                }
            }
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

###############################################
sub get_arrayfromfile {
    open(ARRAY, $_[0]) || die $!;
        @array = <ARRAY>;
    close(ARRAY);
    return (@array);
}

