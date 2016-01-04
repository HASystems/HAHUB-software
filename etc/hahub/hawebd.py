#!/usr/bin/python

import os
import syslog
from flask import Flask, render_template, redirect
import haconfig
import hacmdapi

app = Flask(__name__)

@app.route('/hacmdHTML/v1.3/commands/<command_id>', methods=['GET'])
def run_command(command_id):
	global cmdapi
	global lastcmd
	syslog.syslog(syslog.LOG_INFO, "Command - %s" % command_id)
	cmdapi.runlist([command_id],"at Top Level")
	lastcmd = command_id
	return redirect('/hacmdHTML/v1.3/commands/', code=302)

@app.route('/hacmdHTML/v1.3/commands/', methods=['GET'])
def get_commands():
	global cmdapi
	global lastcmd
	syslog.syslog(syslog.LOG_INFO, "Home Page")
	return render_template('cmdhome.html', commands=sortedcmds(cmdapi.oper_list()), lastone=lastcmd)

@app.route('/')
def index():
	syslog.syslog(syslog.LOG_INFO, "Home Page")
	return render_template('hacmdHTML.html')


@app.route('/hacmdHTML/v1.3/test/', methods=['GET'])
def test_page():
	global cmdapi
	syslog.syslog(syslog.LOG_INFO, "Test Page")
	print "Test Page"
	# print render_template('test.html', commands=sortedcmds(cmdapi.oper_list()))
	return render_template('test.html', commands=sortedcmds(cmdapi.oper_list()))

def sortedcmds(cmdgrplist):
	sortedlist = {}
	for g in cmdgrplist.keys():
		sortedlist[g] = sorted(cmdgrplist[g])
	return sortedlist


# ###############################################################################
# Initialize and start the logging
# ###############################################################################
syslog.openlog("haweb",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))



# ###############################################################################
# Create the pidfile and a log entry for START
# ###############################################################################
mypid = str(os.getpid())
pidfile = open("/var/run/hahub/haweb.pid","w")
pidfile.write(mypid+"\n")
pidfile.close()

syslog.syslog(syslog.LOG_CRIT,"HAWEBD STARTED. PID: "+mypid)



# ###############################################################################
# initialize the hahub objects - Config and CmdAPI
# ###############################################################################
config = haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

cmdapi = hacmdapi.HacmdAPI()
cmdapi.setconfig(config)



# ###############################################################################
# Read the ha.rc files
# ###############################################################################
rcfiles = ["/etc/hahub/ha.rc", "~/.ha.rc", "./ha.rc", "~/bin/ha.rc"]
for rc in rcfiles:
	rcpath = os.path.expanduser(rc)
	if os.access(rcpath, os.R_OK):
		syslog.syslog(syslog.LOG_INFO, "Reading conf from %s" % rcpath)
		cmdapi.readconf(rcpath)



# ###############################################################################
# start the WEB Server
# ###############################################################################
lastcmd = "None"
httpport = config.getConfigIntValue("HTTPPORT", 8080)
app.run(host='0.0.0.0', port=httpport, debug=False)
