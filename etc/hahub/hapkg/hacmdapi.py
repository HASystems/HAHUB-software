#!/usr/bin/python

import syslog
import socket
import time
import string

class HacmdAPI:

	def __init__(self):
		self.cmd_dict = {}
		self.macro_dict = {}
		self.grp_dict = {}
		self.defgrp = "Ungrouped"

	def setconfig(self, config):
		self.config = config

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
			state = 0 # wait BEGIN
			while True:
				ln  = (f.readline()).rstrip('\n')
				if state == 0 and ln == 'BEGIN':
					state = 1 # wait readback the command
				elif state == 1:
					# this line is the command, so just ignore it
					state = 2 # wait for result
				elif state == 2:
					if ln == "SUCCESS":
						# print "Success"
						state = 9 # wait END
					if ln == "ERROR":
						# print "I see error"
						state = 3 # wait DATA
				elif state == 3 and ln == "DATA":
					state = 4 # wait count of error data liner
				elif state == 4:
					c = int(ln)
					for i in range(c):
						syslog.syslog(syslog.LOG_WARNING, "Error: %s" % (f.readline()).rstrip('\n'))
					state = 9 # wait END
				elif state == 9 and ln == 'END':
					break
				else:
					syslog.syslog(syslog.LOG_WARNING, "Unexpected RESPONSE from LIRCD: %s" % ln)
					break
		finally:
			s.close
		return 0

	def runlist(self,cmdlist,tagtxt):
		for opcmd in cmdlist:
			cmdpar = string.split(opcmd,":",1)
			if cmdpar[0] == "delay":
				if cmdpar[1].isdigit():
					nsecs = string.atoi(cmdpar[1])
					if nsecs > 0:
						print "Delaying "+cmdpar[1]+" seconds..."
						time.sleep(nsecs)
			elif self.isop(opcmd):
				cmd =  self.expcmd(opcmd)
				self.irsend(cmd)
				time.sleep(0.5) # this is a hack ... seems U-Verse ignores if same command repeats quickly, e.g., 0 twice quickly
			elif self.ismacro(opcmd):
				newcmdlist = self.expmacro(opcmd)
				self.runlist(newcmdlist,opcmd)
			else:
				syslog.syslog(syslog.LOG_WARNING, "Undefined command: '%s'. (Running %s)." % (opcmd,tagtxt))

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
