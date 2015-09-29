import os
import syslog
from flask import Flask, render_template
import hapkg.haconfig
import hapkg.hacmdapi

app = Flask(__name__)

@app.route('/hacmdapi/v1.3/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
	global cmdapi
	cmdapi.runlist([task_id],"at Top Level")
	return render_template('cmdhome.html', commands=cmdapi.oper_list())

@app.route('/hacmdapi/v1.3/tasks/', methods=['GET'])
@app.route('/')
def index():
	syslog.syslog(syslog.LOG_INFO, "home page")
	print render_template('cmdhome.html', commands=cmdapi.oper_list())
	return render_template('cmdhome.html', commands=cmdapi.oper_list())

@app.route('/power')
def power():
	syslog.syslog(syslog.LOG_INFO, "power page")
	cmdlist = ["allon"]
	cmdapi.runlist(cmdlist,"at Top Level")
	return render_template('power.html')

@app.route('/volumeup')
def volup():
	syslog.syslog(syslog.LOG_INFO, "volup page")
	cmdlist = ["v+"]
	cmdapi.runlist(cmdlist,"at Top Level")
	return render_template('volumeup.html')

@app.route('/volumedown')
def voldown():
	syslog.syslog(syslog.LOG_INFO, "voldn page")
	cmdlist = ["v-"]
	cmdapi.runlist(cmdlist,"at Top Level")
	return render_template('volumedown.html')

syslog.openlog("haweb",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

config = hapkg.haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

cmdapi = hapkg.hacmdapi.HacmdAPI()
cmdapi.setconfig(config)

rcfiles = ["/etc/hahub/ha.rc", "~/.ha.rc", "./ha.rc", "~/bin/ha.rc"]
for rc in rcfiles:
	rcpath = os.path.expanduser(rc)
	if os.access(rcpath, os.R_OK):
		syslog.syslog(syslog.LOG_INFO, "Reading conf from %s" % rcpath)
		cmdapi.readconf(rcpath)

httpport = config.getConfigIntValue("HTTPPORT", 8080)
app.run(host='0.0.0.0', port=httpport, debug=True)
