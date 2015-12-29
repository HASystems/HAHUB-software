#!/usr/bin/python

import syslog
import hapkg.hacmdapi
import os
import sys
import hapkg.haconfig

syslog.openlog("haexec",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))

config = hapkg.haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

hacmdapi = hapkg.hacmdapi.HacmdAPI()
hacmdapi.setconfig(config)

# read the command and macro definitions from *.rc files
rcfiles = ["/etc/hahub/ha.rc", "~/.ha.rc", "./ha.rc", "~/bin/ha.rc"]
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
			if curcmd.isdigit():
				digcmd = []
				for d in curcmd:
					digcmd.append(d)
				hacmdapi.runlist(digcmd,"at Top Level")
			elif curcmd =="list":
				clist = hacmdapi.oper_list()
				for g in sorted(clist.keys()):
					print "Group %s" % g
					prline = ""
					for c in sorted(clist[g]):
						prline = prline + "    %s" % c
					print prline
			elif curcmd == "q":
				exit()
			else:
				hacmdapi.runlist([curcmd],"at Top Level")
