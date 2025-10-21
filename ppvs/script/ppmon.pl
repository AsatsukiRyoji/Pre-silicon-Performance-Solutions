#!/usr/bin/env perl
# ============================================================================ #
#  Copyright (c) 2009-2016 Advanced Micro Devices, Inc.  All rights reserved.  #
# ============================================================================ #


=head1 DESCRIPTION

This tool formats and compares itrace C<*.mon> files from csim and RTL
simulation runs.  Run this command with C<--help> for usage information.

Send questions and bug reports to B<justins> or to B<dl.gfxip.sh>.

=head2 Common Usage

Here are some examples of how this program is used in practice.

=head3 Annotating a single monitor file

    ppmon.pl input.mon

This command interprets, sorts and annotates a single itrace file from
either the csim or RTL model.  The result is printed to standard output and
may be piped into a paginator such as C<less>.  To write the annotated output
to a new file instead, use

    ppmon.pl input.mon -o output.ppmon

To show only the last I<N> instructions of each debug ID (e.g. to determine
what each wavefront was doing at the time of a hang), use the C<--last>
option:

    ppmon.pl --last 5 input.mon

To show only a particular debug ID, use the C<--dbgid>
option:

    ppmon.pl --dbgid 0000000f input.mon

This option supports ranges and lists of debug IDs; see the C<--help> output
for details.  A few quick examples:

    ppmon.pl --dbgid 2,3,5,7 input.mon  # Dump 4 specific IDs
    ppmon.pl --dbgid 8-f input.mon      # Dump IDs in range [0x00000008, 0x0000000f]
    ppmon.pl --dbgid f- input.mon       # Dump IDs starting with 0x0000000f
    ppmon.pl --dbgid -f input.mon       # Dump IDs up to and including 0x0000000f
    ppmon.pl --dbgid 2,3,5,7,8-f input.mon  # Combination of first two examples

To show only a particular thread ID in each wavefront, use the C<--tid>
option (this option supports the same range/list support as C<--dbgid>):

    ppmon.pl --tid 0 input.mon

To inhibit wavefront initialization text, use the C<--noinit> option:

    ppmon.pl --noinit input.mon         # WAVE_START blocks are omitted

To completely remove out noncomparable information (for example, if you want
to diff the itrace output with a third-party tool), use C<-s> (strip):

    ppmon.pl -s input.mon               # Strips out noncomparable information

=head3 Comparing monitor files from two models

    ppmon.pl -d input1.mon input2.mon

This command interprets itrace files from both models, sorts them and
compares the results.  If the itrace files are equivalent after sorting then
it returns an exit code of zero; if the itrace files are different then it
displays the first few mismatching instructions and returns a nonzero exit
code.  The error report includes a brief header explaining the output
followed by the first I<N> errors (error limit configurable on the command
line).  The results are printed to standard output; to write the results
to a new file instead, use

    ppmon.pl -d input1.mon input2.mon -o output.ppmon

This tool is intelligent and will ignore certain lines that cannot be
compared between csim and RTL models in general.  The itrace guide
(itrace.pdf) explains in detail the specific cases that must be ignored.

By default ppmon is aggressive in its comparison; it will check fields that
are deterministic at blocklevel but may not be deterministic at GC level
(for example, CU/SIMD/hardware wave IDs).  If you are checking traces from
a GC test you should add the C<--gc> option to the command line, like so

    ppmon.pl -d input1.mon input2.mon --gc

Certain tests may not be able to check SGPR and VGPR reads at all; for
example tests that are replaying VALU instructions after an exception.
This check can be disabled with the C<--ignore-reads> option, like so

    ppmon.pl -d input1.mon input2.mon --ignore-reads

The maximum number of errors shown in detail can be limited with the
C<--max> command line option, for example to limit to 16 errors use

    ppmon.pl -d input1.mon input2.mon --max 16

=head2  Sample Mismatch in Diff Mode

This is an example of what the output looks like when ppmon diff mode
detects a mismatch between two itrace files.  The output always begins
with a header that helps you understand the output:

    <<< se0sh0_itrace_sim.mon
    >>> se0sh0_itrace_emu.mon
    # Diff letter codes that appear at the beginning of a line:
    # <   line comes from first file listed above.
    # >   line comes from second file listed above.
    # s   line is completely skipped in the check and may not exist on other side.
    # i   line is ignored in the check but must exist on other side.
    # X   error case: line mismatches with other side.
    # A   error case: line is added to the second file and not present in first file.  
    # D   error case: line is deleted from the first file and not present in second file.

The first two lines show the input files being compared and indicate which
file appears on the left (C<< < >>) and which file appears on the right
(C<< > >>).  The remaining lines are a key for later output to help you
understand what was ignored and what actually mismatched.

An error looks like this:

    <<< Error #1, debug ID 00000014, sequence 0000000a (6 lines)
    <   00000014 0000000a: =============================================
    <   00000014 0000000a: VOP1[CU0_SIMD2_WAVE0] TS=332395
    <   00000014 0000000a:   v_readfirstlane_b32  s19, v5
    < i 00000014 0000000a:  active = 1504001500010004
    < i 00000014 0000000a: r [EXEC_HI]15040015 old_sgpr_data TS=332375
    < i 00000014 0000000a: r [EXEC_LO]00010004 old_sgpr_data TS=332375
    >>> Error #1, debug ID 00000014, sequence 0000000a (7 lines)
    >   00000014 0000000a: =============================================
    >   00000014 0000000a: VOP1[CU0_SIMD2_WAVE0] TS=31651
    >   00000014 0000000a:   v_readfirstlane_b32  s19, v5
    > i 00000014 0000000a:  active = 1504001500010004
    >   00000014 0000000a: r [EXEC_HI]15040015 TS=31651
    >   00000014 0000000a: r [EXEC_LO]00010004 TS=31651
    > A 00000014 0000000a: w [S019]ffffff3e TS=31651

This is an example where the file on the right, C<se0sh0_itrace_emu.mon>,
has an extra line that was not found in the file on the left.  The extra
line is marked with the code C<A>.  Some lines were ignored in the
comparison; these lines are still shown but are marked with C<i>.

Note that each
block of output begins with a header, delimited by C<< <<< >> and C<< >>> >>,
giving the error number (starting from 1), the debug and instruction
sequence IDs, and the number of lines of output.

=cut


#use lib "$ENV{OUT_HOME}/$ENV{PROJECT}/common/pub/include/features";
use lib "$ENV{STEM}/pvtb/script";
use strict;
use FileHandle;
use Getopt::Long;
use global_features;


my @opt_filenames;
my $opt_dbgid;
my $opt_diff = 0;
my $opt_gc = 0;
my $opt_help = 0;
my $opt_ignore_reads = 0;
my $opt_last;
my $opt_max  = 5;
my $opt_nodecode;
my $opt_noinit;
my $opt_out;
my $opt_strip;
my $opt_tid;
my $opt_ignore_checksum_reads = 0;
my $opt_dup_wr_to_warn = 0;
my $opt_ignore_checksum_writes = 0;
my $opt_skip_after_xnack = 0;

my $result = GetOptions(
    'dbgid=s'       => \$opt_dbgid,
    'diff|d'        => \$opt_diff,
    'gc'            => \$opt_gc,
    'help|h'        => \$opt_help,
    'ignore-reads'  => \$opt_ignore_reads,
    'last=i'        => \$opt_last,
    'max|m=i'       => \$opt_max,
    'nodecode'      => \$opt_nodecode,
    'noinit'        => \$opt_noinit,
    'out|o=s'       => \$opt_out,
    'strip|s'       => \$opt_strip,
    'tid=s'         => \$opt_tid,
    'skip-after-xnack=i'  => \$opt_skip_after_xnack,
    'ignore-checksumrds'  => \$opt_ignore_checksum_reads,
    'dupwr-to-warn'       => \$opt_dup_wr_to_warn,
    'ignore-checksumwrs'  => \$opt_ignore_checksum_writes,
);
if(!$result || $opt_help) {
    print(<<"EOF");
Usage:  ppmon.pl [options] <itrace-mon-file>
        ppmon.pl [options] -d <itrace-src-file> <itrace-ref-file>

Basic options:
    --diff, -d          Diff two itrace files.
    --gc                Enable GC-level comparison. This mode strips out
                        additional information that is expected to mismatch
                        at the GC level but can be checked at SH blocklevel.
    --help, -h          Display this help.
    --ignore-reads      In diff mode, do not check register reads. May be
                        needed for speculative execution (e.g. exceptions).
    --dupwr-to-warn     Downgrade duplicate vgpr write check to warning.
    --max, -m <N>       Set maximum number of errors to display.
    --ignore-after-xnack <N>  
                        In diff mode, skip sequence numbers after xnack
                        except for "special" sequence numbers used for
                        handlers (others?). Ignores checksums
    --out, -o <file>    Output file (if unspecified, write to stdout).

Filter options:
    --dbgid <list>      Filter output to specified debug IDs only:
                            N           Show only one debug ID.
                            N-M         Show a closed interval of debug IDs.
                            N-          Show all debug IDs starting at N.
                            -M          Show all debug IDs up to and
                                        including M.
                            list1,list2 Combine multiple intervals.
    --last <N>          Display only the last N instructions of each
                        wavefront.
    --nodecode          Do not attempt to decode resource and sampler
                        constants.
    --noinit            Do not display the wave_start/initialization
                        sequences.
    --strip, -s         Strip out output that cannot match (e.g.
                        timestamps). Needed if you are using a third-party
                        diff tool (e.g. tkdiff).
    --tid <list>        Filter output to specified thread IDs only. See
                        --dbgid for the allowed list syntax.

For the full manual please run "perldoc $0".
Questions and bug reports may be sent to justins or to dl.gfxip.sh.

EOF
    exit($result ? 0 : 1);
}
if($opt_diff) {
    if(scalar(@ARGV) != 2) {
        print("Error:  expecting exactly two filenames on the command line.\n");
        exit(1);
    }
} else {
    if(scalar(@ARGV) != 1) {
        print("Error:  expecting exactly one filename on the command line.\n");
        exit(1);
    }
}
@opt_filenames = @ARGV;


## Pull in the register definitions
#BEGIN {
#    my $auto_home = $ENV{'OUT_HOME'};
#    my $project = $ENV{'PROJECT'};
#    defined($auto_home) or die "Cannot find \$OUT_HOME environment variable, aborting";
#    push @INC, "$auto_home/$project/common/pub/include/reg";
#}
use chip_reg_info qw($AR_blocks $AR_reg_info_SQ);


my $out;
my $using_stdout = 0;
my $dp4x_en = 1;

if(defined($opt_out)) {
    $out = new FileHandle($opt_out, "w");
    if(!defined($out)) {
        print("Unable to open output file \"$opt_out\" for write: $!\n");
        exit(1);
    }
} else {
    $out = new_from_fd FileHandle fileno(STDOUT), "w";
    $using_stdout = 1;
}

## TODO : checksums may not match ... any other options to avoid losing this checking??
if ($opt_skip_after_xnack > 0) {
    $opt_ignore_checksum_reads = 1;
    $opt_ignore_checksum_writes = 1;
}

=head1 SUPPORT FUNCTIONS

=head2 C<< @intervals = intervals_of_list($list) >>

Parses a string C<$list> for the dbgid, tid options and returns a list of
closed intervals represented by the input string, such that
C<<$intervals[$i]->[0]>> is the start of an interval and
C<<$intervals[$i]->[1]>> is the end of an interval (inclusive of both
endpoints).  If either endpoint is undefined, the interval is unbounded on
that side.

The list formats are:

=over

=item *

I<N>, single value

=item *

I<N>C<->, range to the end

=item *

C<->I<N>, range from the beginning

=item *

I<N>C<->I<M>, closed interval

=item *

I<list1>C<,>I<list2>, multiple ranges

=back

=cut
sub intervals_of_list {
    my($list) = @_;
    my @intervals;
    for my $interval (split ",", $list) {
        $interval =~ s/^\s+//;
        $interval =~ s/\s+$//;
        next if $interval =~ /^$/;
        if($interval =~ /^(?:0[xX])?([0-9a-fA-F]+)\-(?:0[xX])?([0-9a-fA-F]+)$/) {
            push @intervals, [ $1, $2 ];
        } elsif($interval =~ /^(?:0[xX])?([0-9a-fA-F]+)\-$/) {
            push @intervals, [ $1, undef ];
        } elsif($interval =~ /^\-(?:0[xX])?([0-9a-fA-F]+)$/) {
            push @intervals, [ undef, $1 ];
        } elsif($interval =~ /^(?:0[xX])?([0-9a-fA-F]+)$/) {
            push @intervals, [ $1, $1 ];
        } else {
            print("WARNING: malformed interval \"$interval\" ignored.\n");
        }
    }
    return @intervals;
}


=head2 C<< $result = interval_member($intervalsp, $val) >>

Returns true if the given value C<$val> is a member of the interval list
pointed to by C<$intervalsp>.  See C<intervals_of_list()>.

=cut
sub interval_member {
    my($intervalsp, $val) = @_;
    for my $interval (@$intervalsp) {
        if((!defined($interval->[0]) || $interval->[0] <= $val) &&
           (!defined($interval->[1]) || $val <= $interval->[1]))
        {
            return(1);
        }
    }
    return(0);
}


=head2 C<< cmp_seq($dbgvp) >>

Compare two sequence numbers stored in C<$a> and C<$b>. This comparison is
special in that any sequence number beginning with C<"I"> (short for
"initial") is always sorted before all other sequence numbers.  For normal
sequence numbers sorting is done based on each instruction's timestamp.

=cut
sub cmp_seq {
    my($dbgvp) = @_;
    if($a =~ /^I/) {
        return($b =~ /^I/ ? $a cmp $b : -1);
    } elsif($b =~ /^I/) {
        return(+1);
    } else {
        my $tsa = defined($dbgvp) && defined($dbgvp->{$a}) ? $dbgvp->{$a}->{'timestamp'} : undef;
        my $tsb = defined($dbgvp) && defined($dbgvp->{$b}) ? $dbgvp->{$b}->{'timestamp'} : undef;
        if($tsa != $tsb) {
            return($tsa <=> $tsb);
        } else {
            return($a cmp $b);
        }
    }
};


=head2 C<< $line = map_register_physical_to_logical($line, $sgpr_base, $vgpr_base) >>

Rewrites a C<$line> containing SGPR and VGPR references. The original itrace
file typically contains physical GPR addresses in the compute unit; this
function takes the GPR base allocations and rewrites all GPR references so
they are logical addresses (relative to the initial allocation address).
This function is aware of GPR wraparound in allocations.

The modified line is returned.  The SGPR and VGPR bases can be determined
from the wavefront header.

=cut
sub map_register_physical_to_logical {
    my($line, $sgpr_base, $vgpr_base) = @_;
    if($line =~ /^([^\:]*\:\s*[rw]\s+\[)([^\]]*)(\].*)$/) {
        my($pre, $reg, $post) = ($1, $2, $3);
        if($reg =~ s/^S(\d+)$/$1/) {
            $reg -= $sgpr_base;
            if($reg < 0) {
                $reg += $GLOBAL_FEATURES{'gpu.sq.num_sgpr_per_simd'};
            }
            $line = $pre . sprintf("S%03d", $reg) . $post;
        } elsif($reg =~ s/^V(\d+)/$1/) {
            $reg -= $vgpr_base;
            if($reg < 0) {
                #$reg += (($dp4x_en == 1) ? 2*$GLOBAL_FEATURES{'gpu.sp.num_gprs'} : $GLOBAL_FEATURES{'gpu.sp.num_gprs'});
                $reg += $GLOBAL_FEATURES{'gpu.sp.num_physical_gprs'};
            }
            $line = $pre . sprintf("V%03d", $reg) . $post;
        }
    }
    return($line);
};


=head2 C<< @lines = sort_register_io(@lines) >>

Sort a list of lines for a single instruction to follow a predictable order:

=over

=item 1.

Instruction header is listed first.

=item 2.

All register and state reads are listed second.

=item 3.

All register and state writes are listed last.

=back

Within each group, the order of lines is preserved.  The revised ordering is
returned.

=cut
sub sort_register_io {
    my @lines = @_;
    my $regs;
    my @out_lines;
    for my $line (@lines) {
        if($line =~ /^[^\:]*\:\s*[rw]\s+\[([^\]]*)\](?:\[th([^\]]*)\])?(.)/) {
            my($reg, $thd, $post) = ($1, $2, $3);
            $thd = 64 if !defined($thd);
            $post = "~" if !defined($post);
            $post = ($post =~ /[0-9a-fA-F]/) ? "0" : "~"; # gpr value goes first
            push @{$regs->{$reg}->{$thd}->{$post}}, $line;
        } else {
            push @out_lines, $line;
        }
    }
    for my $reg (sort { $a cmp $b } keys(%$regs)) {
        for my $thd (sort { $a <=> $b } keys(%{$regs->{$reg}})) {
            for my $post (sort { $a cmp $b } keys(%{$regs->{$reg}->{$thd}})) {
                my %lines;
                map {
                    my(undef, $line) = clean_line($_);
                    if ($opt_dup_wr_to_warn) {
                        ## downgrade to warning
                        if (defined($lines{$line}) && ($line =~ /^[^\:]*\:\s+w\s+/)) {
                            print("WARNING: duplicate write \"$lines{$line}\" \n");
                        }
                    } else {
                        ## make line unique if its a dup wr
                        while(defined($lines{$line}) && ($line =~ /^[^\:]*\:\s+w\s+/))
                        { $line++;}
                    }
                    $lines{$line} = $_;
                } @{$regs->{$reg}->{$thd}->{$post}};
                push @out_lines, sort { $a cmp $b } values(%lines);
            }
        }
    }
    return(@out_lines);
};


=head2 C<< $msg = get_seq_string($seqv, $prefix) >>

Print all lines for a given instruction sequence number to the returned
$string; individual lines are stored in the array C<@{$seqv->{'lines'}}>. 
C<$prefix> is an optional string that should be prepended to each line of
output.

=cut
sub get_seq_string {
    my($seqv, $prefix) = @_;
    my $msg;
    for my $line (@{$seqv->{'lines'}}) {
        $msg .= sprintf("%s%s\n", $prefix, $line);
    }
    return $msg;
}


=head2 C<< $msg = get_dbg_string($dbgv, $prefix) >>

Print all instructions for a given debug ID to the returned string;
instructions are stored in the hash of sequence numbers given by C<%$dbgv>. 
C<$prefix> is an optional string prefix that should be prepended to each line
of output.

=cut
sub get_dbg_string {
    my($dbgv, $prefix) = @_;
    my $msg;
    for my $seq (sort { cmp_seq($dbgv) } keys(%$dbgv)) {
        my $seqv = $dbgv->{$seq};
        $msg .= get_seq_string($seqv, $prefix);
    }
    return $msg;
}


=head2 C<< ($compare_code, $line) = clean_line($line) >>

Scrub out noncomparable information in a line and return a status code
indicating whether this line can be checked.  The status code and modified
line of text are returned as a pair.

Information scrubbed from the line:

=over

=item *

Fields in wavefront initialization that are not comparable, such as
LDS and GPR bases, and state ID

=item *

Timestamps

=item *

CU, SIMD and hardware wave ID assignments

=item *

Register read data, if a command line option requests it

=item *

Instruction checksums, if a command line option requests it

=item *

All "PH" lines emitted by itrace

=item *

All lines marked "old_sgpr_data" by itrace

=item *

All active masks (these may be stale in RTL runs due to exec mask
forwarding)

=item *

Wavefront GPR initialization, if a command line option requests it

=item *

Instruction IDs of C<< fffffff[0-9a-f] >>.

=item *

References to S102 and S103 (occurs in rare cases in RTL on scalar memory
operations); these operations are out-of-bounds and will trigger memory
violation, but their reporting cannot be easily avoided in itrace.

=item *

The instruction sequence number itself, which may not match if the
C<skip_check> feature is being used.

=back

Possible status codes are:

=over

=item *

C<"s"> --- skip this line, do not attempt to match it up with any line in
another itrace file

=item *

C<"i"> --- ignore this line; a corresponding ignored line should exist when
comparing with another itrace file, but the contents of the line are not
expected to match

=item *

C<" "> --- check the scrubbed version of this line with another itrace file

=back

=cut
sub clean_line {
    my($line) = @_;
    $line =~ s/((?:lds_base|vgpr_base|sgpr_base)\s*=\s)(\d+,\s*)/$1##,${\(' ' x (length($2) - 3))}/;
    $line =~ s/((?:vgpr_base_msbs)\s*=\s)(\d+)/$1##,${\(' ' x (length($2) - 3))}/; ##skip vgpr base msbs to compare
    if($opt_gc) {
        $line =~ s/((?:state_id)\s*=\s*)(?:0x[0-9a-f]+|\d+)/$1\#\#/g;
    }
    $line =~ s/^[0-9a-fA-F]{8} [0-9a-fA-F]{8}\:/######## ########:/;
    $line =~ s/TS=\w+/TS=\#\#/;
    $line =~ s/\[CU\d+_SIMD\d+_WAVE\d+\]/\[CU\#\#_SIMD\#\#_WAVE\#\#\]/;
    $line =~ /(\/\/\s*[0-9a-fA-F]+\:(?:\s*[0-9a-fA-F]{8}\s*)+$)/;
    my $sp3_addr_comment = $1;
    $line =~ s/\s*\/\/.*//;
    $line .= $sp3_addr_comment;
    if($line =~ /^[0-9a-f]{8} fffffff[0-9a-f]\:/) {
        return('s', $line);
    } elsif($opt_ignore_reads && $line =~ /^[^\:]*\:\s+r\s+/) {
        return('s', $line);
    } elsif($line =~ /replay_dup/){
        return('s', $line);
    } elsif($line =~ /smem_xnack/){
        return('s', $line);
    } elsif($line =~ /vmem_xnack/){
        return('s', $line);
    } elsif(($opt_ignore_reads||$opt_ignore_checksum_reads) && $line =~ /^[^\:]*\:\s+checksum_rd\s*=/) {
        return('i', $line);
    } elsif(($opt_ignore_checksum_writes) && $line =~ /^[^\:]*\:\s+checksum_wr\s*=/){
        return('i', $line);
    } elsif($line =~ /old_sgpr_data/) {
        return('i', $line);
    } elsif($line =~ /active\s+\=/) {
        return('i', $line);
    } elsif($line =~ /^.*\[PH[\d|_]\]/) {
        return('s', $line);
    } elsif($opt_gc && $line =~ /_[sv]data_/) {
        return('s', $line);
    } elsif($line =~ /^[0-9a-fA-F\#]{8} [0-9a-fA-F\#]{8}\:\s*$/) {
        return('s', $line);
    } elsif($line =~ /^.*\[S(?:102|103)\][0-9a-fA-F]{8}/) {
        return('s', $line);
	} else {
        return(' ', $line);
    }
}


=head2 C<< $result = compare_lists($pa, $pb) >>

Compare lines representing a single instruction from two itrace files in
C<@$pa> and C<@$pb>.  This function expect to compare lines for one
instruction at a time, originating from the same debug ID and sequence
number.  Returns true if the two lists of itrace output match after
scrubbing.

The input lines are rewritten in-place to prepend the final comparison
result on a per-line basis.  If a given line matches, two spaces are
prepended.  If the line mismatches then one of the following letter codes
is prepended:

=over

=item *

C<" "> --- line exists on both sides and the scrubbed versions match.

=item *

C<"X"> --- line exists on both sides but does not match.

=item *

C<"D"> --- line exists only in C<@$pa> (deletion from left side).

=item *

C<"A"> --- line exists only in C<@$pb> (addition to right side).

=item *

Other codes from C<clean_line()> are also possible.

=back

=head2 C<< $num_compared >>

Count of total number of lines compared when running in diff mode.

=head2 C<< $num_ignored >>

Count of total number of lines ignored when running in diff mode.

=cut
my $num_compared = 0;
my $num_ignored = 0;
sub compare_lists {
    my($a, $b) = @_;

    my @input = ($a, $b);
    my @skip;
    my @check;
    my @checksize;
    for my $i (0, 1) {
        my $lastidx = $#{$input[$i]};
        my @clean = map {
            my($code, $line) = clean_line($input[$i]->[$_]);
            { 'index' => $_, 'code' => $code, 'line' => $line }
        } (0..$lastidx);
        $skip[$i] = [ grep { $_->{'code'} eq 's' } @clean ];
        $check[$i] = [ grep { $_->{'code'} ne 's' } @clean ];
        $checksize[$i] = scalar(@{$check[$i]});
        $num_compared += scalar(grep { $_->{'code'} eq ' ' } @clean);
        $num_ignored += scalar(grep { $_->{'code'} ne ' ' } @clean);
    }

    my $get_prefix = sub {
        my($s) = @_;
        if($s =~ /([rw]\s+\[[a-zA-Z0-9_]+\](?:\[th\d+\]))/) {
            return($1);
        } else {
            return($s);
        }
    };

    my $find_prefix = sub {
        my($listp, $pos, $prefix) = @_;
        while($pos <= $#$listp) {
            if($listp->[$pos] eq $prefix) {
                return($pos);
            }
            ++$pos;
        }
        return;
    };

    my @prefix;
    for my $i (0, 1) {
        $prefix[$i] = [ map { $get_prefix->($check[$i]->[$_]->{'line'}) } (0..$checksize[$i] - 1) ];
    }

    my @pos = (0, 0);
    my $saw_mismatch = 0;
    while($pos[0] < $checksize[0] && $pos[1] < $checksize[1]) {
        my @s = map { $check[$_]->[$pos[$_]]->{'line'} } (0, 1);
        my @c = map { $check[$_]->[$pos[$_]]->{'code'} } (0, 1);
        if($s[0] eq $s[1] || $c[0] eq 'i' || $c[1] eq 'i') {
            ++$pos[0];
            ++$pos[1];
        } else {
            $saw_mismatch = 1;
            my $ppos;
            if($prefix[0]->[$pos[0]] eq $prefix[1]->[$pos[1]]) {
                # This line is a mismatch.
                map { $check[$_]->[$pos[$_]++]->{'code'} = 'X' } (0, 1);
            } elsif(defined($ppos = $find_prefix->($prefix[0], $pos[0], $prefix[1]->[$pos[1]]))) {
                while($pos[0] < $ppos) {
                    $check[0]->[$pos[0]++]->{'code'} = 'D';
                }
            } elsif(defined($ppos = $find_prefix->($prefix[1], $pos[1], $prefix[0]->[$pos[0]]))) {
                while($pos[1] < $ppos) {
                    $check[1]->[$pos[1]++]->{'code'} = 'A';
                }
            } else {
                map { $check[$_]->[$pos[$_]++]->{'code'} = 'X' } (0, 1);
            }
        }
    }
    map { $check[0]->[$_]->{'code'} = 'D' } ($pos[0]..$checksize[0] - 1);
    map { $check[1]->[$_]->{'code'} = 'A' } ($pos[1]..$checksize[1] - 1);

    for my $i (0, 1) {
        map { $_ = "  " . $_ } @{$input[$i]};
        map { $input[$i]->[$_->{'index'}] =~ s/^./$_->{'code'}/ } (@{$check[$i]}, @{$skip[$i]});
    }
    return($checksize[0] == $checksize[1] && !$saw_mismatch);
}


=head2 C<< @db >>

Database of all itrace data read in by this tool.

An example of this data structure is shown below:

    @db[0] = {
        # Debug IDs
        '00000000' => ...,
        '00000001' => ...,
        '00000002' => {
            # Wave boilerplate
            'INIT' => ...,
            # Instruction IDs
            '00000000' => ...,
            '00000001' => ...,
            '00000002' => {
                'timestamp' => 12345, # timestamp of this instruction, used for sorting
                'lines' => [ ...original input lines... ],
                'inst' => [ 'opcode', 'operand0', 'operand1', ..., 'modifier:value' ],
                'skip_check' => { 0 | 1 }, # skip check for entire instruction if true
                'subseq' => {
                    # Instruction boilerplate
                    '0'  => [ ...input lines... ],
                    # Register read lines
                    'R1' => [ ...input lines... ],
                    # Register write lines
                    'R2' => [ ...input lines... ],
                },
            },
        },
    };

The fields of C<@db> are further described below:

=over

=item C<< $db[$index] >>

Information for the N'th itrace file from the command line.

=item C<< $db[$index]->{$debug_id} = $dbgv >>

Information for a specific C<$debug_id>.  See C<$dbgv> in the
C<get_dbg_string()> function for details on this structure.

=item C<< $dbgv->{$seq_num} = $seqv >>

Information for a specific debug ID and instruction sequence
number, C<$seq_num>.  Note that C<$seq_num> is either the 32-bit
hexadecimal instruction number, or the special token C<"INIT">
to indicate boilerplate for wavefront initialization.

=item C<< $seqv->{'timestamp'} >>

Timestamp for this instruction.

=item C<< $seqv->{'skip_check'} >>

If true, skip this entire instruction for checking and resequence the
instructions that follow.

=item C<< $seqv->{'lines'} >>

Pointer to an array of all lines associated with this debug ID/instruction
ID, in the order they were read from the file.

=item C<< $seqv->{'inst'} >>

Pointer to an array decoding the sp3 instruction for this line, separated
into operands.  The first entry of the array is the opcode, followed by
any operands and modifiers.

=item C<< $seqv->{'subseq'} >>

Pointer to a hash that splits the instruction into sortable components:

=over

=item *

C<< $seqv->{'subseq'}->{'0'} >>

Pointer to array of lines corresponding to the instruction's boilerplate.
This subsequence should always be printed first.

=item *

C<< $seqv->{'subseq'}->{'R1'} >>

Pointer to array of lines of the instruction's register reads.  This
subsequence is always printed second.

=item *

C<< $seqv->{'subseq'}->{'R2'} >>

Pointer to array of lines of the instruction's register writes.  This
subsequence is always printed last.

=item *

C<< $dbgv->{'INIT'}->{'subseq'}->{'1'..'4'} >>

Pointers to lines for the wavefront boilerplate, only appearing for the
C<"INIT"> sequence number.

=back

=back

=cut
my @db;


=head2 C<< @lines = print_rsrc_const($prefix, $type, @words) >>

Decode and print a resource constant. The constant type is given in C<$type>
and should be one of C<"SQ_BUF_RSRC">, C<"SQ_IMG_RSRC"> or C<"SQ_IMG_SAMP">. 
The resource constant dwords are given as integer values in C<@words>.  New
lines of output are returned.

=cut
sub print_rsrc_const {
    my($prefix, $type, @words) = @_;
    my @lines;
    for my $word (0..$#words) {
        push @lines, sprintf("%s# %s_WORD%d", $prefix, $type, $word);
        my $reg = $AR_reg_info_SQ->{"${type}_WORD$word"}->{'fields'};
        for my $field (sort { $reg->{$a}->{'offset'} <=> $reg->{$b}->{'offset'} } keys(%$reg)) {
            my $offset = $reg->{$field}->{'offset'};
            my $size = $reg->{$field}->{'size'};
            my $digits = ($size + 3) / 4;
            my $value = (($words[$word] >> $offset) & ($size == 32 ? 0xffffffff : (1 << $size) - 1));
            my $enum = $reg->{$field}->{'alpha'}->{$value};
            push @lines, sprintf("%s#     %-20s: 0x%0*x %s", $prefix, $field, $digits, $value, defined($enum) ? $enum : "");
        }
    }
    return(@lines);
}


=head2 C<< get_and_print_rsrc_const($dbg, $seq, $seqv, $type, $operand) >>

Identify and decode a resource constant. The debug ID and instruction
sequence information are given, along with the resource constant type. The
operand position (indexed from zero) that contains the constant is given in
C<$operand>.  The new lines of decoded output are added to the instruction
information in C<$seqv>.

=cut
sub get_and_print_rsrc_const {
    my($dbg, $seq, $seqv, $type, $operand) = @_;
    if($seqv->{'inst'}->[$operand + 1] =~ /^s\[(\d+)\:(\d+)\](?:$|\s)/) {
        my $rsrcStart = $1;
        my $rsrcStop = $2;
        my @rsrc;
        for my $regrd (@{$seqv->{'subseq'}->{'R1'}}) {
            if($regrd =~ /r\s+\[S(\d+)\]([0-9a-fA-F]{8})\s+/ && $1 >= $rsrcStart && $1 <= $rsrcStop) {
                $rsrc[$1 - $rsrcStart] = oct("0x$2");
            }
        }
        my @lines = print_rsrc_const("$dbg ${seq}: ", $type, @rsrc);
        push @{$seqv->{'subseq'}->{0}}, @lines;
    }
}


=head2 C<< db_parse_itrace_file($filename, $dbindex) >>

Parse an itrace input file and populate C<$db[$dbindex]> with the contents
of the itrace file.  Terminates the program if an error is encountered.  The
C<%sgpr_base> and C<%vgpr_base> hashes, which track the start address of GPR
allocation for each wave, are reset when this function is called and are
populated with allocation information for each wave in the file.

=cut
my %sgpr_base;
my %vgpr_base;
sub db_parse_itrace_file {
    my($dbindex, $filename) = @_;

    my $fh = new FileHandle($filename, "r");
    defined($fh) or die "Cannot open $filename for read: $!";

    undef(%sgpr_base);
    undef(%vgpr_base);
    undef($dp4x_en);
    while(my $line = $fh->getline()) {
        my($dbg, $seq, $subseq, $timestamp, $skip_check);
        $line =~ s/^\s+//;
        $line =~ s/\s+$//;
        if($line =~ /TS\=(\d+)/) {
            $timestamp = $1;
        }
        if($line =~ /skip_check/) {
            $skip_check = 1;
        }
        if($line =~ /^(\S+)\s+(\S+)\:/) {
            $dbg = $1;
            $seq = $2;
            next if $seq =~ /^fffffffe$/i;
            $subseq = "0";
            if($seq =~ /^\_new\_wv/) {
                $seq = "INIT";
                $subseq = "1";
            } elsif($seq =~ /^\_sdata/) {
                $seq = "INIT";
                $subseq = "2";
            } elsif($seq =~ /^\_vdata/) {
                $seq = "INIT";
                $subseq = "3";
            } elsif($seq =~ /^\_/) {
                $seq = "INIT";
                $subseq = "4";
            } elsif($line =~ /smem_xnack/){
                if($line =~ "smem_xnack=3"){
                    $db[$dbindex]->{$dbg}->{$seq}->{'smem_xnack3_detect'} = 1;
                    $skip_check=1;
                }
                if(($line =~ "smem_xnack=0")&&($db[$dbindex]->{$dbg}->{$seq}->{'smem_xnack3_detect'}==1)){
                    if($db[$dbindex]->{$dbg}->{$seq}->{'skip_check'}==1){
                        $db[$dbindex]->{$dbg}->{$seq}->{'skip_check'} = 0;
                    }
                }
            } elsif($line =~ /vmem_xnack/){ 
                if($line =~ "vmem_xnack=3"){
                    $db[$dbindex]->{$dbg}->{$seq}->{'vmem_xnack3_detect'} = 1;
                    $skip_check=1;
                }
                if($line =~ "vmem_xnack=2"){
                    $db[$dbindex]->{$dbg}->{$seq}->{'vmem_xnack2_detect'} = 1;
                    $skip_check=1;
                }    
                if($line =~ "vmem_xnack=1"){
                    $db[$dbindex]->{$dbg}->{$seq}->{'vmem_xnack1_detect'} = 1;
                }    

                if(($line =~ "vmem_xnack=0")&&($db[$dbindex]->{$dbg}->{$seq}->{'vmem_xnack3_detect'}==1)){
                    if($db[$dbindex]->{$dbg}->{$seq}->{'skip_check'}==1){
                        $db[$dbindex]->{$dbg}->{$seq}->{'skip_check'} = 0;
                    }
                }

                if(($line =~ "vmem_xnack=0")&&($db[$dbindex]->{$dbg}->{$seq}->{'vmem_xnack2_detect'}==1)){
                    if($db[$dbindex]->{$dbg}->{$seq}->{'skip_check'}==1){
                        $db[$dbindex]->{$dbg}->{$seq}->{'skip_check'} = 0;
                    }
                }

            } elsif($line =~ /^[^\:]*\:\s*r/) {
                $subseq = "R1";
            } elsif($line =~ /^[^\:]*\:\s*w/) {
                $subseq = "R2";
            }
            if($line =~ /_new_wv:.*sgpr_base\s*=\s*(\d+)/) {
                $sgpr_base{$dbg} = $1;
            }
            if($line =~ /_new_wv:.*vgpr_base\s*=\s*(\d+)/) {
                $vgpr_base{$dbg} = $1;
            }
            if($line =~ /_new_wv:.*dp4x_en\s*=\s*(\d+)/) {
                $dp4x_en = $1;
            }
            if($line =~ /\:\s{3}([a-zA-Z0-9_]+)(?:\s+(\S.*)|$)/ && !defined($db[$dbindex]->{$dbg}->{$seq}->{'inst'})) {
                $db[$dbindex]->{$dbg}->{$seq}->{'inst'} = [ $1 ];
                my $args = $2;
                $args =~ s/\/\/.*$//;
                while($args =~ s/^\s*((?:[^\,\[]|\[[^\]]*\])+)\,\s*(.*)/$2/) {
                    my $arg = $1;
                    $arg =~ s/^\s+|\s+$//g;
                    push @{$db[$dbindex]->{$dbg}->{$seq}->{'inst'}}, $arg if $arg ne '';
                }
                $args =~ s/^\s+|\s+$//g;
                push @{$db[$dbindex]->{$dbg}->{$seq}->{'inst'}}, $args if $args ne '';
            }
        } else {
            print("WARNING: unknown line \"$line\"\n");
        }
        push @{$db[$dbindex]->{$dbg}->{$seq}->{'subseq'}->{$subseq}}, $line;
        if(defined($timestamp)) {
            if(!defined($db[$dbindex]->{$dbg}->{$seq}->{'timestamp'}) || $timestamp < $db[$dbindex]->{$dbg}->{$seq}->{'timestamp'}) {
                $db[$dbindex]->{$dbg}->{$seq}->{'timestamp'} = $timestamp;
            }
        }
        if($skip_check) {
            $db[$dbindex]->{$dbg}->{$seq}->{'skip_check'} = $skip_check;
        }
    }
    $fh->close();
}


=head2 C<< @dbgids = db_dbg($dbindex) >>

Returns a sorted list of all debug IDs appearing in C<$db[$dbindex]>.

=cut
sub db_dbg {
    my($dbindex) = @_;
    return(sort { $a cmp $b } keys(%{$db[$dbindex]}));
}


=head2 C<< db_filter($dbindex) >>

Filter out unwanted itrace lines in C<$db[$dbindex]> based on arguments
specified on the command line.  This function filters out unwanted debug
IDs, sequence numbers, and thread IDs.

=cut
sub db_filter {
    my($dbindex) = @_;

    # Filter out unwanted debug IDs.
    if(defined($opt_dbgid)) {
        my @intervals = intervals_of_list($opt_dbgid);
        map {
            $_->[0] = oct("0x$_->[0]") if defined($_->[0]);
            $_->[1] = oct("0x$_->[1]") if defined($_->[1]);
        } @intervals;
        for my $dbg (db_dbg($dbindex)) {
            my $dbgval = oct("0x$dbg");
            if(!interval_member(\@intervals, $dbgval)) {
                delete $db[$dbindex]->{$dbg};
            }
        }
    }

    # Filter out unwanted sequence numbers.
    if(defined($opt_noinit)) {
        for my $dbg (db_dbg($dbindex)) {
            my $dbgv = $db[$dbindex]->{$dbg};
            delete $dbgv->{'INIT'};
        }
    }
    if(defined($opt_last)) {
        for my $dbg (db_dbg($dbindex)) {
            my $dbgv = $db[$dbindex]->{$dbg};
            my @seq = sort { cmp_seq($dbgv) } keys(%$dbgv);
            my $num_skip = scalar(@seq) - $opt_last;
            if($num_skip > 0) {
                for my $index (0..$num_skip - 1) {
                    delete $dbgv->{$seq[$index]};
                }
            }
            push @{$db[$dbindex]->{$dbg}->{'INIT'}->{'subseq'}->{0}}, sprintf("%s _info_  : Skipped %d instructions.", $dbg, $num_skip);
        }
    }

    # Filter out ops after xnack 
    if ($opt_skip_after_xnack) {
        my $skip_after_xnack_error=0; ## set when xnack/error deteced
        my $seq_num_xnack_error_inst = 0;
        my $seq_num_mask = 0xffff0000; ## TODO: review proper mask for gfx10, don't skip instructions that may be part of a handler

        for my $dbg (db_dbg($dbindex)) {
            my $dbgv = $db[$dbindex]->{$dbg};
            my @seq = sort { cmp_seq($dbgv) } keys(%$dbgv);
            foreach my $seqnum (@seq) {
                my $seqnum_hex = hex($seqnum);
                if (    ($dbgv->{$seqnum}->{'vmem_xnack1_detect'}>0 && $opt_skip_after_xnack==1) || 
                        ($dbgv->{$seqnum}->{'vmem_xnack2_detect'}>0 && $opt_skip_after_xnack==2) || 
                        ($dbgv->{$seqnum}->{'vmem_xnack3_detect'}>9 && $opt_skip_after_xnack==3)) {
                    $skip_after_xnack_error=1;
                    $seq_num_xnack_error_inst = $seqnum_hex&$seq_num_mask;
                    $out->print(sprintf("detected xnack, will filter out insts after %x (dbindex %x) \n",$seqnum_hex,$dbindex));
                    push(@{$dbgv->{$seqnum}->{'subseq'}->{0}}, sprintf("%s %s: # SKIPPING CHECK AFTER THIS INSTS : REASON SKIP AFTER XNACK FILTERING (vmem_xnack=%d) ",$dbg,$seqnum,$opt_skip_after_xnack));
                } elsif ($skip_after_xnack_error) {
                    if ($seq_num_xnack_error_inst == ($seqnum_hex&$seq_num_mask) ) {
                        $dbgv->{$seqnum}->{'skip_check'}=1;
                        $out->print(sprintf("filter_after_xnack : seqnum %x \n",$seqnum_hex));
                        ## why doesn't this info get printed
                        push(@{$dbgv->{$seqnum}->{'subseq'}->{0}}, sprintf("%s %s: # SKIPPING DUE TO AFTER XNACK FILTERING",$dbg,$seqnum));
                    } else {
                        $skip_after_xnack_error=0;
                        $seq_num_xnack_error_inst=0;
                        $out->print(sprintf("filter_after_xnack : possible handler (will stop skipping) seqnum %x \n",$seqnum_hex));
                    }
                }
            }
        }
    }

    # Filter out unwanted threads.
    if(defined($opt_tid)) {
        my @intervals = intervals_of_list($opt_tid);
        for my $dbg (db_dbg($dbindex)) {
            my $dbgv = $db[$dbindex]->{$dbg};
            for my $seq (sort { cmp_seq($dbgv) } keys(%$dbgv)) {
                my $seqv = $dbgv->{$seq};
                for my $subseq (sort { $a cmp $b } keys(%{$seqv->{'subseq'}})) {
                    my $subseqv = $seqv->{'subseq'}->{$subseq};
                    @$subseqv = grep { $_ !~ /\[th(\d\d)\]/ || interval_member(\@intervals, $1) } @$subseqv;
                }
            }
        }
    }
}


=head2 C<< db_sort_registers($dbindex) >>

In the database C<$db[$dbindex]>, remap physical to logical register numbers
and then sort all register transactions in increasing order.

=cut
sub db_sort_registers {
    my($dbindex) = @_;
    for my $dbg (db_dbg($dbindex)) {
        my $dbgv = $db[$dbindex]->{$dbg};
        for my $seq (sort { cmp_seq($dbgv) } keys(%$dbgv)) {
            my $seqv = $dbgv->{$seq};
            for my $subseq (sort { $a cmp $b } keys(%{$seqv->{'subseq'}})) {
                my $subseqv = $seqv->{'subseq'}->{$subseq};
                @$subseqv = map { map_register_physical_to_logical($_, $sgpr_base{$dbg}, $vgpr_base{$dbg}) } @$subseqv;
                if($subseq =~ /^[R|3]/) {
                    @$subseqv = sort_register_io(@$subseqv);
                }
            }
        }
    }
}


=head2 C<< db_process_replays($dbindex) >>

In the database C<$db[$dbindex]>, remove duplicate lines that are caused by
instruction replay events in an ATC-enabled system.

=cut
sub db_process_replays {
    my($dbindex) = @_;
    for my $dbg (db_dbg($dbindex)) {
        my $dbgv = $db[$dbindex]->{$dbg};
        for my $seq (sort { cmp_seq($dbgv) } keys(%$dbgv)) {
            my $seqv = $dbgv->{$seq};
            for my $subseq (sort { $a cmp $b } keys(%{$seqv->{'subseq'}})) {
                my $subseqv = $seqv->{'subseq'}->{$subseq};
				if($seq ne "INIT" && $subseq !~ /^R/) {
                    my @arr = @$subseqv;
                    my $arrsz = scalar(@arr);
                    my $comm = "replay_dup";
                    my $num_bars;
                    for my $index (0..$arrsz - 1) {
						if($arr[$index] =~ /^[^\:]+\:\s+\=+$/) {
						    ++$num_bars;
					    }
					    if($num_bars >= 2) {
                            $arr[$index] = $comm . $arr[$index];
                        }
                    }
                    @$subseqv = @arr;
                }
            }
        }
    }
}


=head2 C<< db_decode_constants($dbindex) >>

In the database C<$db[$dbindex]>, decode resource and sampler constants if
requested by the user (see command line arguments). Decoded constants are
emitted as comment lines.

=cut
sub db_decode_constants {
    my($dbindex) = @_;
    if(!$opt_nodecode) {
        for my $dbg (db_dbg($dbindex)) {
            my $dbgv = $db[$dbindex]->{$dbg};
            for my $seq (sort { cmp_seq($dbgv) } keys(%$dbgv)) {
                my $seqv = $dbgv->{$seq};
                my $opcode = $seqv->{'inst'}->[0];
                if($opcode =~ /^image_sample/) {
                    get_and_print_rsrc_const($dbg, $seq, $seqv, 'SQ_IMG_RSRC', 2);
                    get_and_print_rsrc_const($dbg, $seq, $seqv, 'SQ_IMG_SAMP', 3);
                } elsif($opcode =~ /^image_/) {
                    get_and_print_rsrc_const($dbg, $seq, $seqv, 'SQ_IMG_RSRC', 2);
                } elsif($opcode =~ /^t?buffer_store_lds_dword/) {
                    get_and_print_rsrc_const($dbg, $seq, $seqv, 'SQ_BUF_RSRC', 0);
                } elsif($opcode =~ /^t?buffer_/) {
                    get_and_print_rsrc_const($dbg, $seq, $seqv, 'SQ_BUF_RSRC', 2);
                } elsif($opcode =~ /^s_buffer_/) {
                    get_and_print_rsrc_const($dbg, $seq, $seqv, 'SQ_BUF_RSRC', 1);
                }
            }
        }
    }
}

sub db_process_vop3r_sgpr {
    my($dbindex) = @_;
    for my $dbg (db_dbg($dbindex)) {
        my $dbgv = $db[$dbindex]->{$dbg};
        for my $seq (sort { cmp_seq($dbgv) } keys(%$dbgv)) {
            my $seqv = $dbgv->{$seq};
            my $opcode = $seqv->{'inst'}->[0];
            if($opcode =~ /.*_r$/){
                #print "VOP3R type inst $opcode\n";
                my $prev_sgpr;
                my $cur_sgpr;
                my @arr;
                for my $subseqrd (@{$seqv->{'subseq'}->{'R1'}}) {
                    if($subseqrd =~ /r\s+\[S(\d{3})\]/ || $subseqrd =~ /r\s+\[VCC_LO\]/ || $subseqrd =~ /r\s+\[VCC_HI\]/ || $subseqrd =~ /r\s+\[EXEC_LO\]/  || $subseqrd =~ /r\s+\[EXEC_HI\]/ ) {
                        $cur_sgpr = $1;
                        if($cur_sgpr eq $prev_sgpr) {
                          #should skip this sgpr read operation,if in vop3r and read the same sgpr, ignore the read data value. Just think its the repeat operation..
                           #print "should delete old sgpr read line: @arr\n";
                        } else {
                           $prev_sgpr = $cur_sgpr;
                           push(@arr,$subseqrd);
                        }
                    } else {
                        push(@arr,$subseqrd);
                    }
                    
                }
                #update vop3r read sgpr array
                @{$seqv->{'subseq'}->{'R1'}} = @arr;
            }
        }
    }
}

=head2 C<< db_generate_lines($dbindex) >>

In the database C<$db[$dbindex]>, generate all of the 'lines' keys for each
sequence that will be used for actual diffing and for pretty-printing the
results.

=cut
sub db_generate_lines {
    my($dbindex) = @_;
    for my $dbg (db_dbg($dbindex)) {
        my $dbgv = $db[$dbindex]->{$dbg};
        for my $seq (sort { cmp_seq($dbgv) } keys(%$dbgv)) {
            my $seqv = $dbgv->{$seq};
            my @lines;
            for my $subseq (sort { $a cmp $b } keys(%{$seqv->{'subseq'}})) {
                my $subseqv = $seqv->{'subseq'}->{$subseq};
                push @lines, @$subseqv;
            }
            if($opt_strip) {
                @lines = map { [ clean_line($_) ] } @lines;
                @lines = grep { $_->[0] !~ /^[si]$/ } @lines;
                @lines = map { $_->[1] } @lines;
            }
            $seqv->{'lines'} = \@lines;
        }
    }
}


for(my $i = 0; $i < scalar(@opt_filenames); ++$i) {
    db_parse_itrace_file($i, $opt_filenames[$i]);
    db_filter($i);
    db_sort_registers($i);
    db_process_replays($i);
    db_decode_constants($i);
    db_process_vop3r_sgpr($i);
    db_generate_lines($i);
}


=head2 C<< $num_errors >>

Total number of errors seen while in diff mode.

=head2 C<< %dbg_errors >>

Hash containing all debug IDs that had at least one error.

=cut
my $num_errors = 0;
my %dbg_errors;


if($opt_diff) {
    my %dbg;
    for(my $i = 0; $i < scalar(@opt_filenames); ++$i) {
        map { ++$dbg{$_} } keys(%{$db[$i]});
    }

    $out->print(<<"EOF");
<<< $opt_filenames[0]
>>> $opt_filenames[1]
# Diff letter codes that appear at the beginning of a line:
# <   line comes from first file listed above.
# >   line comes from second file listed above.
# s   line is completely skipped in the check and may not exist on other side.
# i   line is ignored in the check but must exist on other side.
# X   error case: line mismatches with other side.
# A   error case: line is added to the second file and not present in first file.
# D   error case: line is deleted from the first file and not present in second file.

EOF

    my %dbgid_errors;
    my $log_error = sub {
        my($dbg, $msgfn) = @_;
        ++$num_errors;
        ++$dbg_errors{$dbg};
        if($num_errors <= $opt_max) {
            my $msg = $msgfn->($num_errors);
            $out->print($msg);
            if($num_errors == 1) {
                print($msg);
            }
        }
    };

    for my $dbg (sort { $a cmp $b } keys(%dbg)) {
        if(!defined($db[0]->{$dbg})) {
            $log_error->($dbg, sub {
                "<<< Error #$_[0], debug ID $dbg (missing)\n" .
                ">>> Error #$_[0], Debug ID $dbg\n" .
                get_dbg_string($db[1]->{$dbg}, "> ") . "\n"});
        } elsif(!defined($db[1]->{$dbg})) {
            $log_error->($dbg, sub {
                "<<< Error #$_[0], debug ID $dbg\n" .
                get_dbg_string($db[0]->{$dbg}, "< ") .
                ">>> Error #$_[0], debug ID $dbg (missing)\n\n"});
        } else {
            my @dbgv = ( $db[0]->{$dbg}, $db[1]->{$dbg} );
            my @curseq = map { [ sort { cmp_seq } keys(%{$dbgv[$_]}) ] } (0, 1);
            my @curseqpos = (0, 0);
            my @curseqcnt = map { scalar(@{$curseq[$_]}) } (0, 1);

            while($curseqpos[0] < $curseqcnt[0] || $curseqpos[1] < $curseqcnt[1]) {
                my @seq = map { $curseq[$_]->[$curseqpos[$_]] } (0, 1);
                if($seq[0] =~ /^fffffff[0-9a-f]$/i || $dbgv[0]->{$seq[0]}->{'skip_check'}) {
                    ++$curseqpos[0];
                    next;
                } elsif($seq[1] =~ /^fffffff[0-9a-f]$/i || $dbgv[1]->{$seq[1]}->{'skip_check'}) {
                    ++$curseqpos[1];
                    next;
                } elsif(!defined($dbgv[0]->{$seq[0]})) {
                    $log_error->($dbg, sub {
                        "<<< Error #$_[0], debug ID $dbg, sequence $seq[1] (missing)\n" .
                        ">>> Error #$_[0], debug ID $dbg, sequence $seq[1]\n" .
                        get_seq_string($dbgv[1]->{$seq[1]}, "> ") . "\n"});
                    ++$curseqpos[1];
                    next;
                } elsif(!defined($dbgv[1]->{$seq[1]})) {
                    $log_error->($dbg, sub {
                        "<<< Error #$_[0], debug ID $dbg, sequence $seq[0]\n" .
                        get_seq_string($dbgv[0]->{$seq[0]}, "< ") .
                        ">>> Error #$_[0], debug ID $dbg, sequence $seq[0] (missing)\n\n"});
                    ++$curseqpos[0];
                    next;
                } elsif(!compare_lists($dbgv[0]->{$seq[0]}->{'lines'}, $dbgv[1]->{$seq[1]}->{'lines'})) {
                    $log_error->($dbg, sub {
                        "<<< Error #$_[0], debug ID $dbg, sequence $seq[0] (${\(scalar(@{$dbgv[0]->{$seq[0]}->{'lines'}}))} lines)\n" .
                        get_seq_string($dbgv[0]->{$seq[0]}, "< ") .
                        ">>> Error #$_[0], debug ID $dbg, sequence $seq[1] (${\(scalar(@{$dbgv[1]->{$seq[1]}->{'lines'}}))} lines)\n" .
                        get_seq_string($dbgv[1]->{$seq[1]}, "> ") . "\n"});
                }
                ++$curseqpos[0];
                ++$curseqpos[1];
            }
        }
    }
    $out->printf("\nThere were %d ignored line(s) out of %d total line(s).\n", $num_ignored, $num_compared);
    if(scalar(keys(%dbg_errors)) > 0) {
        $out->print("Debug IDs with errors:\n");
        for my $dbg (sort { $a cmp $b } keys(%dbg_errors)) {
            $out->print("    $dbg\n");
        }
    }
} else {
    for my $dbg (db_dbg(0)) {
        my $dbgv = $db[0]->{$dbg};
        $out->print(get_dbg_string($dbgv, ""));
    }
}


if($num_errors > 0) {
    $out->printf("\nThere were %d ERROR(s)\n\n", $num_errors);
    if(!$using_stdout) {
        printf("There were %d ERROR(s).\n", $num_errors);
    }
    exit(1);
} else {
    exit(0);
}
