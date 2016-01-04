#!/usr/bin/python

import sys

# First add the path of the hahub libraries so they can be imported below
(sys.path).append('/usr/local/lib/hahub')

import syslog
import haconfig
import hawpactrl


syslog.openlog("clear_all_wifi",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

config = haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

wpactrlObj = hawpactrl.WpaCtrl()
wpactrlObj.setconfig(configObj)
wpactrlObj.wpa_open()

wpactrlObj.wpa_clear_networks(self):
