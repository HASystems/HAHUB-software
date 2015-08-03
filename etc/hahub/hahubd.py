#!/usr/bin/python

import hapkg.haconfig
import hapkg.halogger
import hapkg.haledops
import hapkg.haresponder
import hapkg.hawifimon
import threading
import signal
import sys
import os
import time


# ###############################################################################
# create all the utility objects - config, logger, ledops
# ###############################################################################
config = hapkg.haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")

logger = hapkg.halogger.Logger()
cfile = config.getConfigValue("LOGCONFIGFILE", "/etc/hahub/loglevel.conf")
logdir = config.getConfigValue("LOGFILEDIR", "/var/log/hahub")
logbase = "hahubd"
logger.configlogger(cfile, logdir, logbase)

ledops = hapkg.haledops.Ledops()
ledops.setconfig(config)
ledops.setlogger(logger)
ledops.initLEDs()

# ###############################################################################
# Setup signal handler
# ###############################################################################
def cleanup(signum,frame):
	logger.log(5,"Signal received ("+str(signum)+"). Terminating...")
	ledops.cleanupLEDs()
	sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# ###############################################################################
# Create the pidfile and a log entry for START
# ###############################################################################
mypid = str(os.getpid())
pidfile = open("/var/run/hahub/hahub.pid","w")
pidfile.write(mypid+"\n")
pidfile.close()

logger.log(5,"HAHUBD STARTED. PID: "+mypid)

# ###############################################################################
# Start the WiFiMon thread
# ###############################################################################
wifimon = hapkg.hawifimon.Wifimon()
wifimon.setconfig(config)
wifimon.setlogger(logger)
wifimon.setledops(ledops)
twifi = threading.Thread(target=wifimon.run, name="WiFiMon")
twifi.daemon = True
twifi.start()

# ###############################################################################
# Start the responder thread
# ###############################################################################
responder = hapkg.haresponder.Responder()
responder.setconfig(config)
responder.setlogger(logger)
tresp = threading.Thread(target=responder.run, name="Responder")
tresp.daemon = True
tresp.start()

while True:
	if not twifi.is_alive():
		logger.log(5, twifi.name + " Is not alive!!")
	if not tresp.is_alive():
		logger.log(5, tresp.name + " Is not alive!!")
	time.sleep(5)

