#!/usr/bin/python

import socket

bcastsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bcastsock.bind(('', 0))
bcastsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
bcastport = 50001
bcastsock.sendto("PING", ('<broadcast>', bcastport))
bcastsock.close()


rcvaddr = ('', 50000)  # host, port
rcvsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rcvsock.bind(rcvaddr)
data, addr = rcvsock.recvfrom(1024)
print addr[0], "\n"+data

rcvsock.close()

