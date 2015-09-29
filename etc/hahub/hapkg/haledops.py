#!/usr/bin/python

import RPi.GPIO as gpio
import time

class Ledops:
	def __init__(self):
		self.hlthLED = 19
		self.wstsLED = 13
		self.hahubstsLED1 = 5
		self.hahubstsLED2 = 6

	def setconfig(self, config):
		self.config = config

	def initLEDs(self):
		self.hlthLED = self.config.getConfigIntValue("HLTHLED",19)
		self.wstsLED = self.config.getConfigIntValue("WSTSLED",13)
		self.hahubstsLED1 = self.config.getConfigIntValue("HAHUBSTSLED1",5)
		self.hahubstsLED2 = self.config.getConfigIntValue("HAHUBSTSLED2",6)
		gpio.setwarnings(False)
		gpio.setmode(gpio.BCM)
		gpio.setup(self.hlthLED, gpio.OUT)
		gpio.setup(self.wstsLED, gpio.OUT)
		gpio.setup(self.hahubstsLED1, gpio.OUT)
		gpio.setup(self.hahubstsLED2, gpio.OUT)
		for i in range(4):
			gpio.output(self.hlthLED, True)
			gpio.output(self.hahubstsLED1, True)
			gpio.output(self.wstsLED, True)
			gpio.output(self.hahubstsLED2, True)
			time.sleep(0.25)
			gpio.output(self.hlthLED, False)
			gpio.output(self.hahubstsLED1, False)
			gpio.output(self.wstsLED, False)
			gpio.output(self.hahubstsLED2, False)
			time.sleep(0.25)

	def cleanupLEDs(self):
		gpio.cleanup()

	def hlthledon(self):
		gpio.output(self.hlthLED, True)

	def hlthledoff(self):
		gpio.output(self.hlthLED, False)

	def wstsledon(self):
		gpio.output(self.wstsLED, True)

	def wstsledoff(self):
		gpio.output(self.wstsLED, False)



if __name__ == "__main__":
	import haconfig
	config = haconfig.Config()
	config.readConfig("/etc/hahub/hahubd.conf")

	ledops = Ledops()
	ledops.setconfig(config)
	ledops.initLEDs()
	ledops.hlthledon()
	time.sleep(0.25)
	ledops.hlthledoff()
	time.sleep(0.25)
	ledops.wstsledon()
	time.sleep(0.25)
	ledops.wstsledoff()
	time.sleep(0.25)
	ledops.cleanupLEDs()
