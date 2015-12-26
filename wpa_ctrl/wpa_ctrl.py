#!/usr/bin/python

import socket
import os
import string

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

	def wpa_start_PBC(self):
		retval, info = wpa_ctrl.wpa_cmd("WPS_PBC")
		return retval, info

	def wpa_clear_networks(self):
		retval, info = wpa_ctrl.wpa_cmd("LIST_NETWORKS")
		if retval < 0:
			print info
			return retval, info
		nwlist = string.split(info,"\n")[1:]
		allsuccess = True
		for nw in nwlist:
			nwpars = string.split(nw)
			if len(nwpars) > 0:
				nwid = nwpars[0]

				discmd = "DISABLE_NETWORK %s" % nwid
				retval, info = wpa_ctrl.wpa_cmd(discmd)
				if retval < 0:
					print "Error in  ", discmd
					allsuccess = False

				remcmd = "REMOVE_NETWORK %s" % nwid
				retval, info = wpa_ctrl.wpa_cmd(remcmd)
				if retval < 0:
					print "Error in  ", remcmd
					allsuccess = False
		if allsuccess:
			savcmd = "SAVE_CONFIG"
			retval, info = wpa_ctrl.wpa_cmd(savcmd)
			if retval < 0:
				print "Error in  ", savcmd
				return -1, "Error clearing networks. Config not changed"
			else:
				return 0, "Successfully cleared networks"

	def wpa_get_state(self):
		retval, info = wpa_ctrl.wpa_cmd("STATUS")
		if retval < 0:
			print info
			return retval, info
		stspars = string.split(info,"\n")
		ssid = ""
		wpa_state = ""
		for par in stspars:
			parpair = string.split(par,"=")
			if len(parpair) > 1:
				key,val = parpair[:2]
				if key == "ssid":
					ssid=val
				if key == "wpa_state":
					wpa_state = val
		if len(wpa_state) > 0:
			return 0, wpa_state
		else:
			return -1, "Error - wpa_state not found in the returned status"

if __name__ == "__main__":

	wpa_ctrl = Wpa_Ctrl()
	ret = wpa_ctrl.wpa_open()
	if ret < 0:
		print "Error in wpa_open()"

	# retval, info = wpa_ctrl.wpa_cmd("STATUS")
	# if retval < 0:
	# 	print "wpa_cmd: Failed"
	# print info

	retval, info = wpa_ctrl.wpa_get_state()
	if retval < 0:
		print "wpa_cmd: Failed"
	print "Looking up WPA STATE --"
	print info


	# print "List of networks -------"
	# retval, info = wpa_ctrl.wpa_cmd("LIST_NETWORKS")
	# if retval < 0:
	# 	print "wpa_cmd: Failed"
	# print info

	# print "Scanning ..."
	# retval, info = wpa_ctrl.wpa_cmd("SCAN")
	# if retval < 0:
	# 	print "wpa_cmd: Failed"
	# print info

	# retval, info = wpa_ctrl.wpa_cmd("SCAN_RESULTS")
	# if retval < 0:
	# 	print "wpa_cmd: Failed"
	# print info
   
	wpa_ctrl.wpa_close()

	###########################################################################################
	# Tried these, they work, at least for the success paths
	#
	# retval, info = wpa_ctrl.wpa_clear_networks()
	# if retval < 0:
	# 	print "wpa_cmd: Failed"
	# print info
	#
	# print "Start PBC ..."
	# wpa_ctrl.wpa_start_PBC()
	# if retval < 0:
	# 	print "wpa_cmd: Failed"
	# print info

	# Few useful commands - not tried here, but they work with wpa_cli - should use strace to see what wpa_cli sends to wpa_supplicant
	# retval, info = wpa_ctrl.wpa_cmd("LIST_NETWORKS")
	# retval, info = wpa_ctrl.wpa_cmd("ENABLE_NETWORK 0")
	# retval, info = wpa_ctrl.wpa_cmd("PING")
	#
	# REMEMBR to change the sock file location to under /var
	###########################################################################################

