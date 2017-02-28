#Create a simulator object
set ns [new Simulator]

#trace the traffic
$ns trace-all stdout

#Define a 'finish' procedure
proc finish {} {
        global ns
        $ns flush-trace
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

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms $arg1
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail
$ns duplex-link $n4 $n3 10Mb 10ms DropTail

#Set Queue Size of link (n2-n3) to 5
$ns queue-limit $n2 $n3 10

#Setup a TCP connection from N1 to N4
set tcp [new Agent/$arg2]
$tcp set class_ 2
$tcp set window_ 15
$ns attach-agent $n1 $tcp
set sink [if {$arg2 == "Sack1"} {new Agent/TCPSink} {new Agent/TCPSink/Sack1}]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1

#Setup a FTP over TCP connection N1 to N4
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP


#Setup a UDP connection N5 to N6
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null
$udp set fid_ 2

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ 8mb
$cbr set random_ 1

#Schedule events for the CBR and FTP agents
set start [expr 1 + rand()]
$ns at 0.1 "$ftp start"
$ns at $start "$cbr start"

#Call the finish procedure after 10 seconds of simulation time
$ns at 10 "finish"

#Print CBR packet size and interval
puts "CBR packet size = [$cbr set packet_size_]"
puts "CBR interval = [$cbr set interval_]"

#Run the simulation
$ns run
