#!/usr/bin/python

import syslog
import socket
import time
import string

class HacmdAPI:

	################################################################################
	# Data Structures:
	# cmd_dict[cmd]      <-- (remote, [par1, par2, par3, ...])
	# grp_dict[cmd/mac]  <-- grp
	# macro_dict[mac]    <-- [cmd1, cmd2, cmd3, ...]
	################################################################################

	def __init__(self):
		self.cmd_dict = {}
		self.macro_dict = {}
		self.grp_dict = {}
		self.defgrp = "Ungrouped"
		self.slowly = False

	def isop(self,op):
		return self.cmd_dict.has_key(op)

	def ismacro(self,m):
		return self.macro_dict.has_key(m)

	def expmacro(self,m):
		return self.macro_dict[m]

	def expcmd(self,op):
		rem,pars = self.cmd_dict[op]
		cmd = "SEND_ONCE " + rem 
		pstr = ""
		for p in pars:
			pstr = pstr + " " + p
		cmd = cmd + pstr
		return cmd

	#
	# runs the protocol with the LIRC daemon to transmit the command, and receive the response
	# socket is opened and closed each time to avoid any possible 'left over' from the previous command
	#
	def irsend(self,cmd,sim=False):
		if sim:
			syslog.syslog(syslog.LOG_INFO, "irsend: Simulating Command: " + cmd)
			return 0

		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		srvr_addr = self.config.getConfigValue("LIRCDSOCK", "/var/run/lirc/lircd")
		try:
			s.connect(srvr_addr)
		except socket.error, msg:
			syslog.syslog(syslog.LOG_CRIT,"Error writing to LIRCD socket. %s" % msg)
			return -1

		try:
			s.sendall(cmd + "\n")
			f = s.makefile()
			state = 0 # wait for BEGIN
			while True:
				ln  = (f.readline()).rstrip('\n')
				if state == 0 and ln == 'BEGIN':
					state = 1 # wait for readback the command
				elif state == 1:
					# this line is the command, so just ignore it
					state = 2 # wait for result
				elif state == 2:
					if ln == "SUCCESS":
						# print "Success"
						state = 9 # wait for END
					if ln == "ERROR":
						# print "I see error"
						state = 3 # wait for DATA
				elif state == 3 and ln == "DATA":
					state = 4 # wait for count of error data lines
				elif state == 4:
					c = int(ln)
					for i in range(c):
						syslog.syslog(syslog.LOG_WARNING, "Error: %s" % (f.readline()).rstrip('\n'))
					state = 9 # wait for END
				elif state == 9 and ln == 'END':
					break
				else:
					syslog.syslog(syslog.LOG_WARNING, "Unexpected RESPONSE from LIRCD: %s" % ln)
					break
		finally:
			s.close
		return 0

	############################################################################################################
	# API for applications -
	#     setconfig(configObj)  - this is for future, currently no config info is used
	#     readconf(rcfilename)
	#     oper_list()
	#
	# To use this module
	# import hacmdapi
	# ...
	# cmdapiObj = hacmdapi.HacmdAPI()
	# cmdapiObj.setconfig(configObj)  # use the haconfig module to create this configObj
	# ...
	# cmdapiObj.readconf(rcfile1path)
	# cmdapiObj.readconf(rcfile2path)
	# cmdapiObj.readconf(rcfile3path)
	# ...
	# # ... and now use the other API functions of this module to perform the operations
	# cmdapiObj.runlist(CMD_MACRO_list, "at Top Level")
	# grouped_cmdlist = cmdapiObj.oper_list()
	# ...
	############################################################################################################
	# Configuration Information
	#   Key					Default value					Type		Comment
	#	----------------	----------------------------	--------	-------------------------
	#	LIRCDSOCK			/var/run/lirc/lircd				String		Socket address for LIRC daemon
	#
	############################################################################################################

	def setconfig(self, config):
		self.config = config

	#
	# reads run commands files which defines the user commands and macros.
	# Can be called multiple times to consolidate definitions from multiple rc files
	#
	# ha.rc file structure --
	# CMD    group:cmd renmote par1 par2 par3 ...
	# # Comment
	# MACRO  group:mac cmd1 cmd2 cmd3 ...
	#
	def readconf(self,filename):
		f = open(filename,"r")
		linenum = 0
		for rawln in f.readlines():
			linenum += 1
			ln = rawln.strip()
			if len(ln) > 0 and ln[0] != "#":
				lis = ln.split()
				if lis[0] == "CMD":
					cmd = lis[1]
					if cmd.find(":") >= 0:
						(grp,cmd) = cmd.split(":")
					else:
						grp = self.defgrp
					self.grp_dict[cmd] = grp
					rem = lis[2]
					pars = lis[3:]
					self.cmd_dict[cmd] = (rem,pars)
				elif lis[0] == "MACRO":
					m = lis[1]
					if m.find(":") >= 0:
						(grp,m) = m.split(":")
					else:
						grp = self.defgrp
					self.grp_dict[m] = grp
					cmds = lis[2:]
					self.macro_dict[m] = cmds
				else:
					syslog.syslog(syslog.LOG_WARNING, "Error processing file %s. Line %d, Unrecognized: '%s'" % (filename,linenum,ln))
					pass

	#
	# instead of having a function for running 1 command, the function takes and runs a list of commands
	# 'tagtext' is used in the log file entries to indicate the macro being expanded
	#
	def runlist(self,cmdlist,tagtxt):
		for opcmd in cmdlist:
			cmdpar = string.split(opcmd,":",1)
			if cmdpar[0] == "SLOW":
				self.slowly = True
				syslog.syslog(syslog.LOG_INFO, "SLOW flag set to TRUE.")
			elif cmdpar[0] == "NOTSLOW":
				self.slowly = False
				syslog.syslog(syslog.LOG_INFO, "SLOW flag reset to FALSE.")
			elif cmdpar[0] == "delay":
				nsecs = 0
				try:
					nsecs = float(cmdpar[1])
				except ValueError as msg:
					syslog.syslog(syslog.LOG_WARNING, "Error in command: '%s'. (Running %s)." % (opcmd,tagtxt))
				if nsecs > 0:
					syslog.syslog(syslog.LOG_INFO, "Pausing because SLOW flag is set.")
					time.sleep(nsecs)
			elif self.isop(opcmd):
				cmd =  self.expcmd(opcmd)
				self.irsend(cmd)
				if self.slowly:
					time.sleep(0.5) # seems U-Verse ignores if same command repeats quickly, e.g., 0 twice quickly. So use SLOW flag.
			elif self.ismacro(opcmd):
				newcmdlist = self.expmacro(opcmd)
				self.runlist(newcmdlist,opcmd)
			elif opcmd.isdigit():  # makes sense to define CMDs for digit btns as digits, and it better UI to allow 1202 rather than 1 2 0 2
				digcmd = []
				for d in opcmd:
					digcmd.append(d)
				self.runlist(digcmd,"expanding "+opcmd)
			else:
				syslog.syslog(syslog.LOG_WARNING, "Undefined command: '%s'. (Running %s)." % (opcmd,tagtxt))

	# 
	# the returned data structure
	# grouped[grp]       <-- [cmd1, mac2, cmd3, cmd4, mac5, ...]
	#
	def oper_list(self):
		grouped = {}
		for op in self.cmd_dict.keys():
			grp = self.grp_dict[op]
			if grouped.has_key(grp):
				(grouped[grp]).append(op)
			else:
				grouped[grp] = [op]
			# print op
		for op in sorted(self.macro_dict.keys()):
			grp = self.grp_dict[op]
			if grouped.has_key(grp):
				(grouped[grp]).append(op)
			else:
				grouped[grp] = [op]
			# print ">",op
		return grouped

if __name__ == "__main__":
	import os
	import sys
	import hapkg.haconfig

	syslog.openlog("HacmdAPI",0,syslog.LOG_LOCAL0)
	syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))

	config = hapkg.haconfig.Config()
	config.readConfig("/etc/hahub/hahubd.conf")

	hacmdapi = HacmdAPI()
	hacmdapi.setconfig(config)
	rcfiles = ["/etc/hahub/ha.rc", "~/.ha.rc", "./ha.rc", "~/bin/ha.rc"]
	for rc in rcfiles:
		rcpath = os.path.expanduser(rc)
		if os.access(rcpath, os.R_OK):
			syslog.syslog(syslog.LOG_INFO, "Reading conf from %s" % rcpath)
			hacmdapi.readconf(rcpath)
	clist = hacmdapi.oper_list()
	for g in sorted(clist.keys()):
		print "Group %s" % g
		for c in sorted(clist[g]):
			print "    %s" % c
	cmdlist = sys.argv[1:]
	hacmdapi.runlist(cmdlist,"at Top Level")
