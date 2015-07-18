#!/usr/bin/python

import time
import subprocess


class Wifimon:

	def __init__(self):
		self.go = True
		pass

	def setconfig(self, config):
		self.config = config

	def setlogger(self, logger):
		self.logger = logger

	def setledops(self, ledops):
		self.ledops = ledops

	def getwpastate(self):
		e = subprocess.Popen(["/sbin/wpa_cli", "status"], stdout=subprocess.PIPE, universal_newlines=True)
		wpastatus = {}
		for line in e.stdout:
			cleanline = (line.rstrip('\n'))
			if cleanline.find('=') >= 0 :
				(k,v) = cleanline.split('=')
				wpastatus[k] = v
		e.wait()
		return wpastatus['wpa_state']

	def run(self):
		self.logger.log(5,"WIFIMON STARTED.")

		warnbadhlth = self.config.getConfigIntValue("WARNBADHLTH",90)
		critbadhlth = self.config.getConfigIntValue("CRITBADHLTH",120)
		wstsontime = self.config.getConfigIntValue("WSTSONTIME", 2)
		wstsofftime = self.config.getConfigIntValue("WSTSOFFTIME", 3)
		defhlthinc = self.config.getConfigIntValue("DEFHLTHINC", 5)
		maxhlthinc = self.config.getConfigIntValue("MAXHLTHINC", 15)

		badhlth = 0
		while self.go:
			if badhlth > warnbadhlth:
				self.logger.log(5,"Health Status = " + str(badhlth) + ", past Warning Level " + str(warnbadhlth))
				self.ledops.hlthledon()
				if badhlth > critbadhlth:
					self.logger.log(5, "Health Status = " + str(badhlth) + ", past CRITICAL " + str(critbadhlth))
					subprocess.call("reboot")
			else:
				self.ledops.hlthledoff()
			self.ledops.wstsledon()
			time.sleep(wstsontime)
			wifists = self.getwpastate()
			self.logger.log(1, "WiFi WPA Status: " + wifists)
			if wifists != "COMPLETED":
				self.ledops.wstsledoff()
				if wifists == "INACTIVE":
					badhlth = badhlth + defhlthinc
					self.logger.log(3, wifists + ": Restarting PBC...")
					subpriocess.call(["wpa_cli", "wps_pbc"])
				elif wifists == "SCANNING":
					badhlth = badhlth + defhlthinc
				elif wifists == "ASSOCIATED":
					badhlth = badhlth + defhlthinc
				elif wifists == "ASSOCIATING":
					badhlth = badhlth + defhlthinc
				elif wifists == "DISCONNECTED":
					badhlth = badhlth + defhlthinc
				else:
					self.logger.log(3, wifists + ": Unrecognized status found")
					badhlth = badhlth + maxhlthinc
			else:
				badhlth=0
				self.logger.log(1, wifists + " => All good!!")
			time.sleep(wstsofftime)

if __name__ == "__main__":
	import haconfig
	import halogger
	import haledops
	import signal

	config = haconfig.Config()
	config.readConfig("/etc/hahub/hahub.conf")

	logger = halogger.Logger()
	cfile = config.getConfigValue("LOGCONFIGFILE", "/etc/hahub/loglevel.conf")
	logdir = config.getConfigValue("LOGFILEDIR", "/var/log/hahub")
	logbase = config.getConfigValue("LOGFILEBASE", "hahub")
	logger.configlogger(cfile, logdir, logbase)

	ledops = haledops.Ledops()
	ledops.setconfig(config)
	ledops.setlogger(logger)
	ledops.initLEDs()

	def cleanup(signum, frame):
		logger.log(5,"Signal received: "+str(signum))
		ledops.cleanupLEDs()
		quit()
	signal.signal(signal.SIGTERM, cleanup)
	signal.signal(signal.SIGINT, cleanup)

	wifimon = Wifimon()
	wifimon.setconfig(config)
	wifimon.setlogger(logger)
	wifimon.setledops(ledops)
	wifimon.run()
