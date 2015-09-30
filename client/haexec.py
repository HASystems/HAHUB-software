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
