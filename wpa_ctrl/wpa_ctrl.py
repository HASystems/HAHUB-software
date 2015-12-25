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

	###########################################################################################
	# Tried it, it works 
	# print "Start PBC ..."
	# retval, info = wpa_ctrl.wpa_cmd("WPS_PBC")
	# if retval < 0:
	# 	print "wpa_cmd: Failed"
	# print info

	# Few useful commands - not tried here, but they work with wpa_cli - should use strace to see what wpa_cli sends to wpa_supplicant
	# retval, info = wpa_ctrl.wpa_cmd("LIST_NETWORKS")
	# retval, info = wpa_ctrl.wpa_cmd("ENABLE_NETWORK 0")
	# retval, info = wpa_ctrl.wpa_cmd("DISABLE_NETWORK 1")
	# retval, info = wpa_ctrl.wpa_cmd("REMOVE_NETWORK 1")
	# retval, info = wpa_ctrl.wpa_cmd("SAVE_CONFIG")

	# To get the status
	# retval, info = wpa_ctrl.wpa_cmd("STATUS")
	# It returns a multi-line text in info:
	#     Selected interface 'wlan0'
	#     bssid=74:44:01:99:cc:04
	#     ssid=RenuAtul-Library
	#     id=0
	#     mode=station
	#     pairwise_cipher=CCMP
	#     group_cipher=CCMP
	#     key_mgmt=WPA2-PSK
	#     wpa_state=COMPLETED
	#     ip_address=192.168.0.109
	#     address=00:13:ef:40:0b:b6
	# so need to write code to pick out the "wpa_state" value to show the status via the LEDs
	###########################################################################################

	wpa_ctrl.wpa_close()
