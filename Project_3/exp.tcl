#Create a simulator object
set ns [new Simulator]

<<<<<<< HEAD
# #Define different colors for data flows (for NAM)
# $ns color 1 Blue
# $ns color 2 Red

#Open the NAM trace file
# set nf [open out.nam w]
# $ns namtrace-all $nf

set traceFile [open exp1-trace.tr w]
$ns trace-all $traceFile
$ns trace-all stdout

#Define a 'finish' procedure
=======
>>>>>>> 7cf5eae9115df53631792882e829b913ff66dbac
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

#Retrieve the command line arguments
set arg1 [lindex $argv 0] 
set arg2 [lindex $argv 1]

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail

#trace the traffic between n2 and n3
$ns trace-queue $n2 $n3 stdout

#Set Queue Size of link (n2-n3) to 5
$ns queue-limit $n2 $n3 5

#Setup a TCP connection
set tcp [new Agent/$arg1]
$tcp set class_ 2
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP


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
$cbr set rate_ $arg2
$cbr set random_ false

#Schedule events for the CBR and FTP agents
$ns at 0.1 "$cbr start"
$ns at 1.0 "$ftp start"
$ns at 8.0 "$ftp stop"
$ns at 9.0 "$cbr stop"

#Call the finish procedure after 10 seconds of simulation time
$ns at 10 "finish"

#Print CBR packet size and interval
puts "CBR packet size = [$cbr set packet_size_]"
puts "CBR interval = [$cbr set interval_]"

#Run the simulation
$ns run