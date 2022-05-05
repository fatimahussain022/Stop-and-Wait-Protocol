# Stop-and-Wait-Protocol
This stop-and-wait protocol is a transport layer protocol built on top of the User Datagram Protocol (UDP). It allows a client/server communication where the client can send files and the server can accept, save and acknowledge these files. The main goal is reliable transfer of files. Hence, it implements the basic principles of Reliable Data Transfer (RDT). 

As UDP is too reliable in this case (ironically), the Badnet is used to drop, duplicate, corrupt, lose and deliver out of order packets. Each Badnet class has a different behavior that can be used to test the program. 

The code was written entirely in Python (version 3.9) using the PyCharm IDE (version 2020.3 Community Edition).

It has been tested to transmit files of upto 2 MB successfully.
With a few changes the code can be run on Linux. 
