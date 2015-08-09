#!/usr/bin/python

import socket
import string

class GetHAHUB:
	def __init__(self):
		pass

	def getHAHUB(self):
		retval = False

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
		self.IPaddr = addr[0]
		# print addr[0], "\n"+data

		# Initialize the data packet KEYs per the protocol
		# To be modified if the data format changes
		self.resp_info = {}
		lines = string.split(data, "\n")
		for l in lines:
			if len(l) > 0:
				(key,val) = string.split(l,"=")
				self.resp_info[key] = val
		prod = self.resp_info["PRODUCT"]
		verno = self.resp_info["VERSION"]
		print "Product   :\t", prod, "v" + verno
		print "At IP     :\t", self.IPaddr
		print "HTTP Port :\t", self.resp_info["HTTPPORT"]
		print "Time      :\t", self.resp_info["UTC"], "UTC"

		rcvsock.close()

		return retval

if __name__ == "__main__":
	gethahub = GetHAHUB()
	gethahub.getHAHUB()
