default:
	chmod 755 exp1.java
	chmod 755 exp2.java
	chmod 755 exp3.java
	javac exp1.java
	javac exp2.java
	javac exp3.java
	java exp1 TCP
	java exp1 TCP/Reno
	java exp1 TCP/Newreno
	java exp1 TCP/Vegas
	java exp2 TCP/Reno TCP/Reno
	java exp2 TCP/Reno TCP/Newreno
	java exp2 TCP/Vegas TCP/Vegas
	java exp2 TCP/Newreno TCP/Vegas
	java exp3 DropTail TCP/Reno
	java exp3 RED TCP/Sack1
	java exp3 DropTail TCP/Reno
	java exp3 RED TCP/Sack1
clean:
	rm -f *.class

