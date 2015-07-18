#!/usr/bin/python

import socket
import time

class Responder:
	def __init__(self):
		self.go = True

	def setconfig(self, config):
		self.config = config

	def setlogger(self, logger):
		self.logger = logger

	def sendbcast(self):
		prod = self.config.getConfigValue("PRODUCT","HAHUB")
		ver = self.config.getConfigValue("VERSION","1.3")
		data = "PRODUCT="+prod+"\n"+"VERSION="+ver+"\n"+"UTC="+repr(time.time())+"\n"

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
		self.logger.log(1, "Received Request From: '%s', msg: '%s'" % (addr[0], data))

	def run(self):
		self.logger.log(5,"RESPONDER STARTED.")
		while self.go:
			self.logger.log(1, "Waiting to receive a response request ...")
			self.rcvbcast()
			for i in range(5):
				time.sleep(0.25)
				self.logger.log(1, "Responding ...")
				self.sendbcast()


if __name__ == "__main__":
	import haconfig
	import halogger

	logger = halogger.Logger()
	logger.configlogger("/etc/hahub/loglevel.conf", "/var/log/hahub", "hahub")

	config = haconfig.Config()
	config.readConfig("/etc/hahub/hahub.conf")

	resp = Responder()
	resp.setconfig(config)
	resp.setlogger(logger)
	resp.run()
