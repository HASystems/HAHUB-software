#!/usr/bin/python

import time
import subprocess
import syslog
import hawpactrl
import threading

class Wifimon:

	def __init__(self):
		self.go = True
		self.lock = threading.Lock()
		self.wpactrl = None
		pass

	###############################################################################################
	# For internal use. Wrapper functions for calling WPA command functions
	###############################################################################################

	def getwpastate(self):
		retval, state = self.wpactrl.wpa_get_state()
		if retval < 0:
			syslog.syslog(syslog.LOG_CRIT,"Error getting WPA state - %s" % state)
			return "INACTIVE"  # just return some bad state
		return state

	def restart_PBC(self):
		self.lock.acquire()
		syslog.syslog(syslog.LOG_INFO,"Restart_PBC called ....")
		retval,info = self.wpactrl.wpa_start_PBC()
		if retval < 0:
			syslog.syslog(syslog.LOG_CRIT,"Error starting PBC - %s" % info)
		self.lock.release()

	###############################################################################################
	# Usage of this module:
	# 
	# import hawifimon
	# ...
	# wifimonObj = hawifimon.Wifimon()
	# wifimonObj.setconfig(configObj)  # use the haconfig module to create this configObj
	# wifimonObj.setgpioops(gpioopsObj)  # use the hagpioops module to create this gpioopsObj
	# ...
	# 
	# # Now start the wifimon.run() function in a thread
	# import threading
	# twifi = threading.Thread(target=wifimonObj.run, name="WiFiMon")
	# twifi.daemon = True
	# twifi.start()
	# 
	###############################################################################################

	###############################################################################################
	# API to inject the config object and GPIOops object
	###############################################################################################

	def setconfig(self, config):
		self.config = config

	def setgpioops(self, gpioops):
		self.gpioops = gpioops

	###############################################################################################
	# API for the main WiFi Monitoring thread
	###############################################################################################

	def run(self):
		syslog.syslog(syslog.LOG_CRIT,"WIFIMON STARTED.")

		warnbadhlth = self.config.getConfigIntValue("WARNBADHLTH",90)
		critbadhlth = self.config.getConfigIntValue("CRITBADHLTH",120)
		wifipolltime = self.config.getConfigIntValue("WIFIPOLLTIME", 5)
		defhlthinc = self.config.getConfigIntValue("DEFHLTHINC", 5)
		maxhlthinc = self.config.getConfigIntValue("MAXHLTHINC", 15)

		self.wpactrl = hawpactrl.WpaCtrl()
		self.wpactrl.setconfig(self.config) 

		badhlth = 0
		while self.go:
			if badhlth > warnbadhlth:
				syslog.syslog(syslog.LOG_CRIT,"Health Status = " + str(badhlth) + ", past Warning Level " + str(warnbadhlth))
				self.gpioops.setLEDon(self.gpioops.hlthLED)
				if badhlth > critbadhlth:
					syslog.syslog(syslog.LOG_CRIT, "Health Status = " + str(badhlth) + ", past CRITICAL " + str(critbadhlth))
					subprocess.call("reboot")
			else:
				self.gpioops.setLEDoff(self.gpioops.hlthLED)
			wifists = self.getwpastate()
			syslog.syslog(syslog.LOG_INFO, "WiFi WPA Status: " + wifists)
			if wifists != "COMPLETED":
				self.gpioops.setLEDtoggle(self.gpioops.wstsLED)
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
				self.gpioops.wstsledon()
				syslog.syslog(syslog.LOG_INFO, wifists + " => All good!!")
			time.sleep(wifipolltime)

if __name__ == "__main__":
	import haconfig
	import hagpioops
	import signal

	config = haconfig.Config()
	config.readConfig("/etc/hahub/hahubd.conf")


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
