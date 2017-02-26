# Experiment 1

set tcp_id [lindex $argv 0]
set cbr_bw [lindex $argv 1]

set ns [new Simulator]

#set namFile [open "test-nam.nam" w]
#$ns namtrace-all $namFile

$ns trace-all stdout

proc finish {} {
    global ns
    $ns flush-trace
    #close $namFile
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

set tcp1_start [expr 5 * rand()]
set buffer_size [expr int(10 + 40 * rand())]
$ns queue-limit $n2 $n3 $buffer_size

# Add CBR Flow
set udp [new Agent/UDP]
set udpSink [new Agent/Null]
set cbr0 [new Application/Traffic/CBR]
$udp set class_ 0
$udp set fid_ 0
$ns attach-agent $n2 $udp
$ns attach-agent $n3 $udpSink
$ns connect $udp $udpSink
# Configure CBR Bandwidth
$cbr0 attach-agent $udp
$cbr0 set rate_ ${cbr_bw}Mb
$cbr0 set random_ 1

# Add TCP1 Flow
set tcp [new $tcp_id]
set tcpSink [new Agent/TCPSink]
set ftp [new Application/FTP]
set cbr1 [new Application/Traffic/CBR]
$tcp set class_ 1
$cbr1 set fid_ 1
$ns attach-agent $n1 $tcp
$ns attach-agent $n4 $tcpSink
$ns connect $tcp $tcpSink
# Add Traffic to TCP Flow
$cbr1 attach-agent $tcp
$cbr1 set rate_ 5Mb
$cbr1 set random_ 1

if {$cbr_bw > 0} { $ns at 0 "$cbr0 start" }
$ns at $tcp1_start "$cbr1 start"
$ns at 20 "finish"

$ns run