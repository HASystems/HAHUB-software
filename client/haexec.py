#!/usr/bin/python

import socket
import sys
import time

class Haexec:

	def __init__(self):
		self.cmd_dict = {}
		self.macro_dict = {}
		self.grp_dict = {}
		self.defgrp = "Ungrouped"

	def setconfig(self, config):
		self.config = config

	def setlogger(self, logger):
		self.logger = logger

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
					self.logger.log(3, "Error processing file %s. Line %d, Unrecognized: '%s'" % (filename,linenum,ln))

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
			self.logger.log(1, "irsend Simulating.")
			self.logger.log(1, "irsend: Command: " + cmd)
			return

		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		srvr_addr = self.config.getConfigValue("LIRCDSOCK", "/var/run/lirc/lircd")
		try:
			s.connect(srvr_addr)
		except socket.error, msg:
			sys.exit(1)

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
						print "Error: %s" % (f.readline()).rstrip('\n')
					state = 9 # wait END
				elif state == 9 and ln == 'END':
					break
				else:
					print "Unexpected RESPONSE from LIRCD: %s" % ln
					break
		finally:
			s.close

	def runlist(self,cmdlist,tagtxt):
		for opcmd in cmdlist:
			if self.isop(opcmd):
				cmd =  self.expcmd(opcmd)
				self.irsend(cmd)
				time.sleep(0.5) # this is a hack ... seems U-Verse ignores if same command repeats quickly, e.g., 0 twice quickly
			elif self.ismacro(opcmd):
				newcmdlist = self.expmacro(opcmd)
				self.runlist(newcmdlist,opcmd)
			else:
				print "Undefined command: '%s'. (Running %s)." % (opcmd,tagtxt)

	def oper_list(self):
		grouped = {}
		for op in cmd_dict.keys():
			grp = grp_dict[op]
			if grouped.has_key(grp):
				(grouped[grp]).append(op)
			else:
				grouped[grp] = [op]
			# print op
		for op in sorted(macro_dict.keys()):
			grp = grp_dict[op]
			if grouped.has_key(grp):
				(grouped[grp]).append(op)
			else:
				grouped[grp] = [op]
			# print ">",op
		return grouped

if __name__ == "__main__":
	import os
	import hapkg.haconfig
	import hapkg.halogger

	config = hapkg.haconfig.Config()
	config.readConfig("/etc/hahub/hahubd.conf")

	logger = hapkg.halogger.Logger()
	logger.configlogger("/etc/hahub/loglevel.conf", "/var/log/hahub", "haexec")

	haexec = Haexec()
	haexec.setconfig(config)
	haexec.setlogger(logger)
	rcfiles = ["/etc/hahub/ha.rc", "~/.ha.rc", "./ha.rc", "~/bin/ha.rc"]
	for rc in rcfiles:
		rcpath = os.path.expanduser(rc)
		if os.access(rcpath, os.R_OK):
			print "Reading conf from", rcpath
			haexec.readconf(rcpath)
	cmdlist = sys.argv[1:]
	haexec.runlist(cmdlist,"at Top Level")
