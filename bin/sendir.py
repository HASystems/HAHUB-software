#!/usr/bin/python

import socket
import sys
import time

cmd_dict = {}

def readconf(filename):
	global cmd_dict
	f = open(filename,"r")
	for ln in f.readlines():
		lis = ln.split()
		c = lis[0]
		rem = lis[1]
		pars = lis[2:]
		cmd_dict[c] = (rem,pars)

def isvalidop(op):
	return cmd_dict.has_key(op)

def mkcmd(op):
	rem,pars = cmd_dict[op]
	cmd = "SEND_ONCE " + rem 
	pstr = ""
	for p in pars:
		pstr = pstr + " " + p
	cmd = cmd + pstr
	return cmd

def irsend(cmd):
	print "irsend: received command: " + cmd
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
					print "Success"
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
				print "UNEXPECTED INPUT: %s" % ln
				break
	finally:
		s.close


if __name__ == "__main__":
	readconf("ha.device.conf")
	op = sys.argv[1]
	if isvalidop(op):
		cmd =  mkcmd(op)
		irsend(cmd)
