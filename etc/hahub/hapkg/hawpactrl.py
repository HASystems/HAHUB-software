#!/usr/bin/python

################################################################
# WPA Control API
# To be used in hawifimin.py for performing any control
# actions for the wifi network management
################################################################

import socket
import os
import syslog
import string

class WpaCtrl:

	def __init__(self):
		self.srvr_addr = "/var/run/wpa_supplicant/wlan0"
		# self.ctrl_addr_template = "/var/run/hahub/sock_wpa_ctrl_%d"
		self.ctrl_addr_template = "/home/pi/dev/client/sock_wpa_ctrl_%d"
		self.ctrl_addr = self.ctrl_addr_template % os.getpid()
		self.sock = None
		self.isOpen = False
		self.config = None


	#########################################################################################
	# This is the core API
	# To use this module do the following
	#
	# import hawpactrl
	# ...
	# wpactrlObj = hawpactrl.GPIOops()
	# wpactrlObj.setconfig(configObj)  # use the haconfig module to create this configObj
	# wpactrlObj.wpa_open()
	# ...
	# # ... and now use the other API functions of this module to perform the operations
	#
	#########################################################################################

	def setconfig(self, config):
		self.config = config
		# and read all the required config parameters here
		self.srvr_addr = self.config.getConfigValue("WPASRVEADDR","/var/run/wpa_supplicant/wlan0")
		self.ctrl_addr_template = self.config.getConfigValue("WPACTRLADDRTMPLT","/var/run/hahub/sock_wpa_ctrl_%d")
		self.ctrl_addr = self.ctrl_addr_template % os.getpid()

	def wpa_open(self):
		syslog.syslog(syslog.LOG_INFO, "Attempting to open socket connection to wpa_supplicant")
		try:
			if os.path.exists(self.ctrl_addr):
				os.remove(self.ctrl_addr)
			self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			self.sock.bind(self.ctrl_addr)
		except socket.error, msg:
			syslog.syslog(syslog.LOG_WARNING, "wpa_open() Error binding to local address %s" % msg)
			os.remove(self.ctrl_addr)
			return -1
		self.isOpen = True
		syslog.syslog(syslog.LOG_INFO, "Opened WPA socket connection to wpa_supplicant")
		return 0

	#
	# Use this to gracefully close the socket. Not using it will leave a socket file left behind.
	#
	def wpa_close(self):
		self.sock.close()
		os.remove(self.ctrl_addr)
		self.isOpen = False

	#########################################################################################
	# This is a generic API for any wpa operation, it returns success/failure and information text
	#########################################################################################

	def wpa_cmd(self, cmd):
		syslog.syslog(syslog.LOG_INFO, "WPA command: <%s>" % cmd)
		if self.isOpen != True:
			retval = self.wpa_open()
			if retval < 0:
				return -1, "wpa_open() failed"
		try:
			l = self.sock.sendto(cmd, self.srvr_addr)
		except socket.error, msg:
			syslog.syslog(syslog.LOG_WARNING, "WPA command: <%s> failed with <%s>" % (cmd,msg))
			return -1, errmsg
		resp, srvr = self.sock.recvfrom(2048)
		syslog.syslog(syslog.LOG_INFO, "WPA command: <%s> successful" % cmd)

		return 0, resp

	#########################################################################################
	# These are more macro level operations - 
	# clear all registered wifi n/w
	# start PBC
	# get wifi connection state
	#########################################################################################

	def wpa_clear_networks(self):
		syslog.syslog(syslog.LOG_INFO, "WPA command: <%s>" % "wpa_clear_networks()")
		retval, info = self.wpa_cmd("LIST_NETWORKS")
		if retval < 0:
			return retval, info
		nwlist = string.split(info,"\n")[1:]
		allsuccess = True
		for nw in nwlist:
			nwpars = string.split(nw)
			if len(nwpars) > 0:
				nwid = nwpars[0]

				discmd = "DISABLE_NETWORK %s" % nwid
				retval, info = self.wpa_cmd(discmd)
				if retval < 0:
					allsuccess = False

				remcmd = "REMOVE_NETWORK %s" % nwid
				retval, info = self.wpa_cmd(remcmd)
				if retval < 0:
					allsuccess = False
		if allsuccess:
			syslog.syslog(syslog.LOG_INFO, "WPA command: <%s> saving config" % "wpa_clear_networks()")
			savcmd = "SAVE_CONFIG"
			retval, info = self.wpa_cmd(savcmd)
			if retval < 0:
				syslog.syslog(syslog.LOG_WARNING, "WPA command: <%s> FAILED while saving config" % "wpa_clear_networks()")
				return -1, "Error clearing networks. Config not changed"
			else:
				syslog.syslog(syslog.LOG_INFO, "WPA command: <%s> successful" % "wpa_clear_networks()")
				return 0, "Successfully cleared networks"

	def wpa_start_PBC(self):
		syslog.syslog(syslog.LOG_INFO, "WPA command: <%s>" % "wpa_start_PBC()")
		retval, info = self.wpa_cmd("WPS_PBC")
		return retval, info

	def wpa_get_state(self):
		syslog.syslog(syslog.LOG_INFO, "WPA command: <%s>" % "wpa_get_state()")
		retval, info = self.wpa_cmd("STATUS")
		if retval < 0:
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
			syslog.syslog(syslog.LOG_INFO, "WPA command: <%s> successful" % "wpa_get_state()")
			return 0, wpa_state
		else:
			syslog.syslog(syslog.LOG_WARNING, "WPA command: <%s> FAILED" % "wpa_get_state()")
			return -1, "Error - wpa_state not found in the returned status"

if __name__ == "__main__":

	wpa_ctrl = WpaCtrl()
	ret = wpa_ctrl.wpa_open()
	if ret < 0:
		print "Error in wpa_open()"

	# retval, info = wpa_ctrl.wpa_cmd("STATUS")
	# if retval < 0:
	# 	print "wpa_cmd: Failed"
	# print info

	print "Clearing up all WiFi Networks--"
	retval, info = wpa_ctrl.wpa_clear_networks()
	if retval < 0:
		print "wpa_cmd: Failed"
	print info

	print "Looking up WPA STATE --"
	retval, info = wpa_ctrl.wpa_get_state()
	if retval < 0:
		print "wpa_cmd: Failed"
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

