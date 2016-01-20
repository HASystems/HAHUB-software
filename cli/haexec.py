#!/usr/bin/python

import syslog
import hacmdapi
import os
import sys
import haconfig

syslog.openlog("haexec",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))

config = haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

hacmdapi = hacmdapi.HacmdAPI()
hacmdapi.setconfig(config)

# read the command and macro definitions from *.rc files
rcfiles = ["/etc/hahub/ha.rc", "~/.ha.rc", "~/bin/ha.rc", "./ha.rc"]
for rc in rcfiles:
	rcpath = os.path.expanduser(rc)
	if os.access(rcpath, os.R_OK):
		syslog.syslog(syslog.LOG_INFO, "Reading conf from %s" % rcpath)
		hacmdapi.readconf(rcpath)

# Run any commands given on the command line
cmdlist = sys.argv[1:]
hacmdapi.runlist(cmdlist,"at Top Level")

# take and execute commands interactively
while True:
	sys.stdout.write("> ")
	cmdline = sys.stdin.readline()
	cmdlist = cmdline.split()

	if len(cmdlist) == 0:
		pass
	else:
		for curcmd in cmdlist:
			if curcmd =="list" or curcmd == "l":
				syslog.syslog(syslog.LOG_INFO, "Executong command; %s" % curcmd)
				clist = hacmdapi.oper_list()
				for g in sorted(clist.keys()):
					print "Group %s" % g
					prline = ""
					for c in sorted(clist[g]):
						prline = prline + "    %s" % c
					print prline
			elif curcmd == "?":
				syslog.syslog(syslog.LOG_INFO, "printing help")
				print "Commands:"
				print "l	- list all commands"
				print "list	- list all commands"
				print "q	- quit"
				print "?	- print help (this text)"
				print "any command as listed by 'list' command"
			elif curcmd == "q":
				syslog.syslog(syslog.LOG_INFO, "Quitting")
				exit()
			else:
				syslog.syslog(syslog.LOG_INFO, "Executong command; %s" % curcmd)
				hacmdapi.runlist([curcmd],"at Top Level")
