import os
import syslog
from flask import Flask, render_template
import haconfig
import hacmdapi

app = Flask(__name__)

@app.route('/hacmdapi/v1.3/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
	global cmdapi
	syslog.syslog(syslog.LOG_INFO, "Command - %s" % task_id)
	print "Command - %s" % task_id
	cmdapi.runlist([task_id],"at Top Level")
	# return render_template('cmdhome.html', commands=sortedcmds(cmdapi.oper_list()))
	return redirect('/hacmdapi/v1.3/tasks/', code=302)

@app.route('/hacmdapi/v1.3/tasks/', methods=['GET'])
@app.route('/')
def index():
	global cmdapi
	syslog.syslog(syslog.LOG_INFO, "Home Page")
	print "Home Page"
	return render_template('cmdhome.html', commands=sortedcmds(cmdapi.oper_list()))

@app.route('/hacmdapi/v1.3/test/', methods=['GET'])
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

syslog.openlog("haweb",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

config = haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

cmdapi = hacmdapi.HacmdAPI()
cmdapi.setconfig(config)

rcfiles = ["/etc/hahub/ha.rc", "~/.ha.rc", "./ha.rc", "~/bin/ha.rc"]
for rc in rcfiles:
	rcpath = os.path.expanduser(rc)
	if os.access(rcpath, os.R_OK):
		syslog.syslog(syslog.LOG_INFO, "Reading conf from %s" % rcpath)
		cmdapi.readconf(rcpath)

httpport = config.getConfigIntValue("HTTPPORT", 8080)
app.run(host='0.0.0.0', port=httpport, debug=True)
