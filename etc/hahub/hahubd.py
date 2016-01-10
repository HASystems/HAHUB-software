#!/usr/bin/python

import haconfig
import hagpioops
import haresponder
import hawifimon
import syslog
import threading
import signal
import sys
import os
import time


# ###############################################################################
# create all the utility objects - config, gpioops, open syslog
# ###############################################################################
syslog.openlog("hahubd",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))

config = haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

gpioops = hagpioops.GPIOops()
gpioops.setconfig(config)
gpioops.initGPIOs()

# ###############################################################################
# Setup signal handler
# ###############################################################################
def cleanup(signum,frame):
	syslog.syslog(syslog.LOG_CRIT,"Signal received ("+str(signum)+"). Terminating...")
	gpioops.cleanupGPIOs()
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
# Setup callback for FUNC button to shutdown the OS
# ###############################################################################
def callback_Halt_System(btn):
	syslog.syslog(syslog.LOG_WARNING, "Responding to FUNC button press. Shuttng down...")
	os.execv("/sbin/halt", ["/sbin/halt"])
gpioops.callback_funcbtn_onrising(callback_Halt_System)

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
wifimon = hawifimon.Wifimon()
wifimon.setconfig(config)
wifimon.setgpioops(gpioops)
def callback_restart_PBC(btn):
	syslog.syslog(syslog.LOG_WARNING, "Responding to WPS button press")
	wifimon.restart_PBC()
gpioops.callback_wpsbtn_onrising(callback_restart_PBC)
twifi = threading.Thread(target=wifimon.run, name="WiFiMon")
twifi.daemon = True
twifi.start()

# ###############################################################################
# Start the responder thread
# ###############################################################################
responder = haresponder.Responder()
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

