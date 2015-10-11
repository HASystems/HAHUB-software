#!/usr/bin/python

import socket
import os

class Wpa_Ctrl:

	def __init__(self):
		self.srvr_addr = "/var/run/wpa_supplicant/wlan0"
		# ctrl_addr_template = "/var/run/hahub/sock_wpa_ctrl_%d"
		self.ctrl_addr_template = "/home/pi/dev/wpa_ctrl/sock_wpa_ctrl_%d"
		self.ctrl_addr = self.ctrl_addr_template % os.getpid()
		self.sock = None
		self.isOpen = False

	def wpa_open(self):
		try:
			if os.path.exists(self.ctrl_addr):
				os.remove(self.ctrl_addr)
			self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			self.sock.bind(self.ctrl_addr)
		except socket.error, msg:
			print "Error binding to local address %s" % msg
			os.remove(self.ctrl_addr)
			return -1
		self.isOpen = True
		return 0

	def wpa_close(self):
		self.sock.close()
		os.remove(self.ctrl_addr)
		self.isOpen = False

	def wpa_cmd(self, cmd):
		if self.isOpen != True:
			return -1, "Wpa_Ctrl connection not open. Call wpa_open() first."
		try:
			l = self.sock.sendto(cmd, self.srvr_addr)
		except socket.error, msg:
			errmsg = "Error sending to wpa_supplicant. %s" % msg
			print errmsg
			return -1, errmsg
		resp, srvr = self.sock.recvfrom(2048)

		return 0, resp


if __name__ == "__main__":

	wpa_ctrl = Wpa_Ctrl()
	ret = wpa_ctrl.wpa_open()
	if ret < 0:
		print "Error in wpa_open()"

	retval, info = wpa_ctrl.wpa_cmd("STATUS")
	if retval < 0:
		print "wpa_cmd: Failed"
	print info

	retval, info = wpa_ctrl.wpa_cmd("LIST_NETWORKS")
	if retval < 0:
		print "wpa_cmd: Failed"
	print info

	print "Scanning ..."
	retval, info = wpa_ctrl.wpa_cmd("SCAN")
	if retval < 0:
		print "wpa_cmd: Failed"
	print info

	retval, info = wpa_ctrl.wpa_cmd("SCAN_RESULTS")
	if retval < 0:
		print "wpa_cmd: Failed"
	print info

	wpa_ctrl.wpa_close()
