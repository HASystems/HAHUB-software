#!/usr/bin/python

import hapkg.haconfig
import hapkg.haledops
import hapkg.haresponder
import hapkg.hawifimon
import syslog
import threading
import signal
import sys
import os
import time


# ###############################################################################
# create all the utility objects - config, ledops, open syslog
# ###############################################################################
syslog.openlog("hahubd",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))

config = hapkg.haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

ledops = hapkg.haledops.Ledops()
ledops.setconfig(config)
ledops.initLEDs()

# ###############################################################################
# Setup signal handler
# ###############################################################################
def cleanup(signum,frame):
	syslog.syslog(syslog.LOG_CRIT,"Signal received ("+str(signum)+"). Terminating...")
	ledops.cleanupLEDs()
	sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def chloglevel(signum,frame):
	if signum == signal.SIGUSR1:
		syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))
		syslog.syslog(syslog.LOG_WARNING,"Signal received ("+str(signum)+"). Setting logging level to WARNING.")
	if signum == signal.SIGUSR2:
		syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))
		syslog.syslog(syslog.LOG_INFO,"Signal received ("+str(signum)+"). Setting logging level to INFO.")

signal.signal(signal.SIGUSR1, chloglevel)
signal.signal(signal.SIGUSR2, chloglevel)

# ###############################################################################
# Create the pidfile and a log entry for START
# ###############################################################################
mypid = str(os.getpid())
pidfile = open("/var/run/hahub/hahub.pid","w")
pidfile.write(mypid+"\n")
pidfile.close()

syslog.syslog(syslog.LOG_CRIT,"HAHUBD STARTED. PID: "+mypid)

# ###############################################################################
# Start the WiFiMon thread
# ###############################################################################
wifimon = hapkg.hawifimon.Wifimon()
wifimon.setconfig(config)
wifimon.setledops(ledops)
twifi = threading.Thread(target=wifimon.run, name="WiFiMon")
twifi.daemon = True
twifi.start()

# ###############################################################################
# Start the responder thread
# ###############################################################################
responder = hapkg.haresponder.Responder()
responder.setconfig(config)
tresp = threading.Thread(target=responder.run, name="Responder")
tresp.daemon = True
tresp.start()

while True:
	if not twifi.is_alive():
		syslog.syslog(syslog.LOG_CRIT, twifi.name + " Is not alive!!")
	if not tresp.is_alive():
		syslog.syslog(syslog.LOG_CRIT, tresp.name + " Is not alive!!")
	time.sleep(5)

