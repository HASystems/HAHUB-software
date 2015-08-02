#!/usr/bin/python

import socket
import sys
import time

cmd_dict = {}
macro_dict = {}
grp_dict = {}
defgrp = "Ungrouped"

def readconf(filename):
	global cmd_dict
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
					grp = defgrp
				grp_dict[cmd] = grp
				rem = lis[2]
				pars = lis[3:]
				cmd_dict[cmd] = (rem,pars)
			elif lis[0] == "MACRO":
				m = lis[1]
				if m.find(":") >= 0:
					(grp,m) = m.split(":")
				else:
					grp = defgrp
				grp_dict[m] = grp
				cmds = lis[2:]
				macro_dict[m] = cmds
			else:
				print "Error processing file %s. Line %d, Unrecognized: '%s'" % (filename,linenum,ln)

def isop(op):
	return cmd_dict.has_key(op)

def ismacro(m):
	return macro_dict.has_key(m)

def expmacro(m):
	return macro_dict[m]

def excmd(op):
	rem,pars = cmd_dict[op]
	cmd = "SEND_ONCE " + rem 
	pstr = ""
	for p in pars:
		pstr = pstr + " " + p
	cmd = cmd + pstr
	return cmd

def irsend(cmd,sim=False):
	if sim:
		print "irsend Simulating."
		print "irsend: Command: " + cmd
		return

	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	srvr_addr = "/var/run/lirc/lircd"
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

def runlist(cmdlist,tagtxt):
	for opcmd in cmdlist:
		if isop(opcmd):
			cmd =  excmd(opcmd)
			irsend(cmd)
			time.sleep(0.5)
			# irsend(cmd,sim=True)
		elif ismacro(opcmd):
			newcmdlist = expmacro(opcmd)
			runlist(newcmdlist,opcmd)
		else:
			print "Undefined command: '%s'. (Running %s)." % (opcmd,tagtxt)

def oper_list():
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
	readconf("/etc/hahub/ha.rc")
	cmdlist = sys.argv[1:]
	runlist(cmdlist,"at Top Level")
