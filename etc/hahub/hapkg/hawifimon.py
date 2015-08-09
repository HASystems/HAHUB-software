#!/usr/bin/python

import time
import subprocess
import syslog

class Wifimon:

	def __init__(self):
		self.go = True
		pass

	def setconfig(self, config):
		self.config = config

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
		syslog.syslog(syslog.LOG_CRIT,"WIFIMON STARTED.")

		warnbadhlth = self.config.getConfigIntValue("WARNBADHLTH",90)
		critbadhlth = self.config.getConfigIntValue("CRITBADHLTH",120)
		wstsontime = self.config.getConfigIntValue("WSTSONTIME", 2)
		wstsofftime = self.config.getConfigIntValue("WSTSOFFTIME", 3)
		defhlthinc = self.config.getConfigIntValue("DEFHLTHINC", 5)
		maxhlthinc = self.config.getConfigIntValue("MAXHLTHINC", 15)

		badhlth = 0
		while self.go:
			if badhlth > warnbadhlth:
				syslog.syslog(syslog.LOG_CRIT,"Health Status = " + str(badhlth) + ", past Warning Level " + str(warnbadhlth))
				self.ledops.hlthledon()
				if badhlth > critbadhlth:
					syslog.syslog(syslog.LOG_CRIT, "Health Status = " + str(badhlth) + ", past CRITICAL " + str(critbadhlth))
					subprocess.call("reboot")
			else:
				self.ledops.hlthledoff()
			self.ledops.wstsledon()
			time.sleep(wstsontime)
			wifists = self.getwpastate()
			syslog.syslog(syslog.LOG_INFO, "WiFi WPA Status: " + wifists)
			if wifists != "COMPLETED":
				self.ledops.wstsledoff()
				if wifists == "INACTIVE":
					badhlth = badhlth + defhlthinc
					syslog.syslog(syslog.LOG_WARNING, wifists + ": Restarting PBC...")
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
					syslog.syslog(syslog.LOG_WARNING, wifists + ": Unrecognized status found")
					badhlth = badhlth + maxhlthinc
			else:
				badhlth=0
				syslog.syslog(syslog.LOG_INFO, wifists + " => All good!!")
			time.sleep(wstsofftime)

if __name__ == "__main__":
	import haconfig
	import haledops
	import signal

	config = haconfig.Config()
	config.readConfig("/etc/hahub/hahub.conf")


	ledops = haledops.Ledops()
	ledops.setconfig(config)
	ledops.initLEDs()

	def cleanup(signum, frame):
		syslog.syslog(syslog.LOG_CRIT,"Signal received: "+str(signum))
		ledops.cleanupLEDs()
		quit()
	signal.signal(signal.SIGTERM, cleanup)
	signal.signal(signal.SIGINT, cleanup)

	wifimon = Wifimon()
	wifimon.setconfig(config)
	wifimon.setledops(ledops)
	wifimon.run()
