# Experiment 2
# This experiment tests TCP variant against each other for fairness.
#
# The network is an H pattern with a 10 Mbps CBR over the bridge,
# and one TCP over the top and bottom.
#
# Variants compared are as follows:
# Reno/Reno
# NewReno/Reno
# Vegas/Vegas
# NewReno/Vegas

set tcp1_id [lindex $argv 0]
set tcp2_id [lindex $argv 1]
set cbr_bw [lindex $argv 2]

set ns [new Simulator]

$ns trace-all stdout

proc finish {} {
    global ns
    $ns flush-trace
    exit 0
}

set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

$ns color 1 Blue
$ns color 2 Red

$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

$ns duplex-link-op $n3 $n6 orient right-down
$ns duplex-link-op $n3 $n4 orient right-up
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n2 $n3 queuePos 0.5
$ns duplex-link-op $n5 $n2 orient right-up
$ns duplex-link-op $n1 $n2 orient right-down

set tcp1_start [expr 10 * rand()]
set tcp2_start [expr 10 * rand()]

# Add CBR Flow
set udp [new Agent/UDP]
set udpSink [new Agent/Null]
set cbr [new Application/Traffic/CBR]
$udp set class_ 0
$udp set fid_ 0
$ns attach-agent $n2 $udp
$ns attach-agent $n3 $udpSink
$ns connect $udp $udpSink
# Configure CBR Bandwidth
$cbr attach-agent $udp
$cbr set rate_ ${cbr_bw}Mb
$cbr set random_ 1

# Add TCP1 Flow
set tcp1 [new Agent/$tcp1_id]
set tcp1Sink [new Agent/TCPSink]
set ftp1 [new Application/FTP]
$tcp1 set class_ 1
$ftp1 set fid_ 1
$ns attach-agent $n1 $tcp1
$ns attach-agent $n4 $tcp1Sink
$ns connect $tcp1 $tcp1Sink
# Add Traffic to TCP1 Flow
$ftp1 attach-agent $tcp1

# Add TCP2 Flow
set tcp2 [new Agent/$tcp2_id]
set sink2 [new Agent/TCPSink]
set ftp2 [new Application/FTP]
$tcp2 set class_ 2
$tcp2 set fid_ 2
$ns attach-agent $n5 $tcp2
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
# Add Traffic to TCP2 Flow
$ftp2 attach-agent $tcp2

if {$cbr_bw > 0} { $ns at 0 "$cbr start" }
$ns at $tcp1_start "$ftp1 start"
$ns at $tcp2_start "$ftp2 start"
$ns at 30 "finish"

$ns run