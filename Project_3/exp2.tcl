#Create a simulator object
set ns [new Simulator]

#Define different colors for data flows (for NAM)
$ns color 1 Blue
$ns color 2 Red

#Open the NAM trace file
# set nf [open out.nam w]
# $ns namtrace-all $nf

set traceFile2 [open test-trace2.tr w]
$ns trace-all $traceFile2

#Define a 'finish' procedure
proc finish {} {
        global ns nf traceFile2
        $ns flush-trace
        #Close the NAM trace file
        # close $nf
        close $traceFile2
        exit 0
}

#Create four nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Retrieve the command line arguments
set arg1 [lindex $argv 0] 
set arg2 [lindex $argv 1]
set arg3 [lindex $argv 2]

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail
$ns duplex-link $n4 $n3 10Mb 10ms DropTail

#Set Queue Size of link (n2-n3) to 10
$ns queue-limit $n2 $n3 10

#Give node position (for NAM)
# $ns duplex-link-op $n0 $n2 orient right-down
# $ns duplex-link-op $n1 $n2 orient right-up
# $ns duplex-link-op $n2 $n3 orient right

#Monitor the queue for link (n2-n3). (for NAM)
# $ns duplex-link-op $n2 $n3 queuePos 0.5


#Setup a TCP connection from N1 to N4
set tcp [new Agent/$arg1]
$tcp set class_ 2
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1

#Setup a TCP connection from N5 to N6
set tcp1 [new Agent/$arg2]
$tcp1 set class_ 3
$ns attach-agent $n5 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n6 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 3

#Setup a FTP over TCP connection N1 to N4
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP

#Setup a FTP over TCP connection N5 to N6
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null
$udp set fid_ 2

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ $arg3
$cbr set random_ false


#Schedule events for the CBR and FTP agents
$ns at 0.1 "$cbr start"
$ns at 1.0 "$ftp start"
$ns at 1.0 "$ftp1 start"
$ns at 8.0 "$ftp stop"
$ns at 8.0 "$ftp1 stop"
$ns at 9.0 "$cbr stop"

#Detach tcp and sink agents (not really necessary)
# $ns at 4.5 "$ns detach-agent $n0 $tcp ; $ns detach-agent $n3 $sink"

#Call the finish procedure after 5 seconds of simulation time
$ns at 10 "finish"

#Print CBR packet size and interval
puts "CBR packet size = [$cbr set packet_size_]"
puts "CBR interval = [$cbr set interval_]"

#Run the simulation
$ns run
