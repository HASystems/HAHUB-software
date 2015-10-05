#!/usr/bin/python

import time
import subprocess
import syslog
import threading

class Wifimon:

	def __init__(self):
		self.go = True
		self.lock = threading.Lock()
		pass

	def setconfig(self, config):
		self.config = config

	def setgpioops(self, gpioops):
		self.gpioops = gpioops

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

	def restart_PBC(self):
		self.lock.acquire()
		syslog.syslog(syslog.LOG_INFO,"Restart_PBC called ....")
		subprocess.call(["wpa_cli", "wps_pbc"])
		self.lock.release()

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
				self.gpioops.hlthledon()
				if badhlth > critbadhlth:
					syslog.syslog(syslog.LOG_CRIT, "Health Status = " + str(badhlth) + ", past CRITICAL " + str(critbadhlth))
					subprocess.call("reboot")
			else:
				self.gpioops.hlthledoff()
			self.gpioops.wstsledon()
			time.sleep(wstsontime)
			wifists = self.getwpastate()
			syslog.syslog(syslog.LOG_INFO, "WiFi WPA Status: " + wifists)
			if wifists != "COMPLETED":
				self.gpioops.wstsledoff()
				if wifists == "INACTIVE":
					badhlth = badhlth + defhlthinc
					syslog.syslog(syslog.LOG_WARNING, wifists + ": Restarting PBC...")
					self.restart_PBC()
				elif wifists == "SCANNING":
					syslog.syslog(syslog.LOG_WARNING, wifists)
					badhlth = badhlth + defhlthinc
				elif wifists == "ASSOCIATED":
					syslog.syslog(syslog.LOG_WARNING, wifists)
					badhlth = badhlth + defhlthinc
				elif wifists == "ASSOCIATING":
					syslog.syslog(syslog.LOG_WARNING, wifists)
					badhlth = badhlth + defhlthinc
				elif wifists == "DISCONNECTED":
					syslog.syslog(syslog.LOG_WARNING, wifists)
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
	import hagpioops
	import signal

	config = haconfig.Config()
	config.readConfig("/etc/hahub/hahub.conf")


	gpioops = hagpioops.GPIOops()
	gpioops.setconfig(config)
	gpioops.initGPIOs()

	def cleanup(signum, frame):
		syslog.syslog(syslog.LOG_CRIT,"Signal received: "+str(signum))
		gpioops.cleanupGPIOs()
		quit()
	signal.signal(signal.SIGTERM, cleanup)
	signal.signal(signal.SIGINT, cleanup)

	wifimon = Wifimon()
	wifimon.setconfig(config)
	wifimon.setgpioops(gpioops)
	wifimon.run()
