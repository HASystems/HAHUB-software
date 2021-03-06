#!/usr/bin/python

import socket
import time
import syslog

class Responder:
	def __init__(self):
		self.go = True

	############################################################################################################
	# This responds to broadcast query messages send on REQ_BCASTPORT (default 50001)
	# The response structure is text
	#	PRODUCT=<PRODUCT>
	#   VERSION=<VERSION>
	#   HTTPPORT=<HTTPPORT>
	#   UTC=repr(time.time())
	# all the <> are substituted by the values for those keynames from the config info
	#
	# To use this module do the following
	#
	# import haresponder
	# ...
	# respObj = haresponder.Responder()
	# respObj.setconfig(configObj)  # use the haconfig module to create this configObj
	# ...
	# 
	# # Now start the respObj.run() function in a thread
	# import threading
	# tresp = threading.Thread(target=respObj.run, name="Responder")
	# tresp.daemon = True
	# tresp.start()
	#
	############################################################################################################
	# Configuration Information
	#   Key					Default value					Type		Comment
	#	----------------	----------------				--------	-------------------------
	#	PRODUCT				HAHUB							String		Product name to broadcast
	#	VERSION				1.3								String		Version name to broadcast
	#	HTTPPORT			5000							String		HTTP port to broadcast (as string)
	#	RES_BCASTPORT		50000							Integer		Port # to broadcast response
	#	REQ_BCASTPORT		50001							Integer		Port # to receive request
	#
	############################################################################################################

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
