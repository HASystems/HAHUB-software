#!/usr/bin/python

import socket
import time
import syslog

class Responder:
	def __init__(self):
		self.go = True

	def setconfig(self, config):
		self.config = config

	def sendbcast(self):
		prod = self.config.getConfigValue("PRODUCT","HAHUB")
		ver = self.config.getConfigValue("VERSION","1.3")
		httpport = self.config.getConfigValue("HTTPPORT","5000")
		data = "PRODUCT="+prod+"\n"+"VERSION="+ver+"\n"+"HTTPPORT="+httpport+"\n"+"UTC="+repr(time.time())+"\n"

		bcastsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		bcastsock.bind(('', 0))
		bcastsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		bcastport = self.config.getConfigIntValue("RES_BCASTPORT",50000)
		bcastsock.sendto(data, ('<broadcast>', bcastport))
		bcastsock.close()

	def rcvbcast(self):
		rcvsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		rcvport = self.config.getConfigIntValue("REQ_BCASTPORT",50001)
		rcvsock.bind(('',rcvport))
		data, addr = rcvsock.recvfrom(1024)
		syslog.syslog(syslog.LOG_INFO, "Received Request From: '%s', msg: '%s'" % (addr[0], data))

	def run(self):
		syslog.syslog(syslog.LOG_CRIT,"RESPONDER STARTED.")
		while self.go:
			syslog.syslog(syslog.LOG_INFO, "Waiting to receive a response request ...")
			self.rcvbcast()
			for i in range(5):
				time.sleep(0.25)
				syslog.syslog(syslog.LOG_INFO, "Responding ...")
				self.sendbcast()


if __name__ == "__main__":
	import haconfig

	syslog.openlog("hahubd",0,syslog.LOG_LOCAL0)

	config = haconfig.Config()
	config.readConfig("/etc/hahub/hahubd.conf")

	resp = Responder()
	resp.setconfig(config)
	resp.run()
