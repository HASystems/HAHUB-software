#!/usr/bin/python

import RPi.GPIO as gpio
import time

class GPIOops:
	def __init__(self):
		self.hlthLED = 19
		self.wstsLED = 13
		self.hahubstsLED1 = 5
		self.hahubstsLED2 = 6
		self.wpsbtn = 17
		self.funcbtn = 27

	def setconfig(self, config):
		self.config = config

	def initGPIOs(self):
		self.hlthLED = self.config.getConfigIntValue("HLTHLED",19)
		self.wstsLED = self.config.getConfigIntValue("WSTSLED",13)
		self.hahubstsLED1 = self.config.getConfigIntValue("HAHUBSTSLED1",5)
		self.hahubstsLED2 = self.config.getConfigIntValue("HAHUBSTSLED2",6)
		self.wpsbtn = self.config.getConfigIntValue("WPS_BTN",17)
		self.funcbtn = self.config.getConfigIntValue("FUNC_BTN",27)
		gpio.setwarnings(False)
		gpio.setmode(gpio.BCM)
		gpio.setup(self.hlthLED, gpio.OUT)
		gpio.setup(self.wstsLED, gpio.OUT)
		gpio.setup(self.hahubstsLED1, gpio.OUT)
		gpio.setup(self.hahubstsLED2, gpio.OUT)
		gpio.setup(self.wpsbtn, gpio.IN)
		gpio.setup(self.funcbtn, gpio.IN)
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

	def cleanupGPIOs(self):
		gpio.cleanup()

	def hlthledon(self):
		gpio.output(self.hlthLED, True)

	def hlthledoff(self):
		gpio.output(self.hlthLED, False)

	def wstsledon(self):
		gpio.output(self.wstsLED, True)

	def wstsledoff(self):
		gpio.output(self.wstsLED, False)


	def callback_wpsbtn_onrising(self, callback_fn):
		gpio.add_event_detect(self.wpsbtn, gpio.RISING, callback=callback_fn)

	def callback_wpsbtn_onfalling(self, callback_fn):
		gpio.add_event_detect(self.wpsbtn, gpio.FALLING, callback=callback_fn)

	def callback_wpsbtn_onboth(self, callback_fn):
		gpio.add_event_detect(self.wpsbtn, gpio.BOTH, callback=callback_fn)

	def callback_funcbtn_onrising(self, callback_fn):
		gpio.add_event_detect(self.funcbtn, gpio.RISING, callback=callback_fn)

	def callback_funcbtn_onfalling(self, callback_fn):
		gpio.add_event_detect(self.funcbtn, gpio.FALLING, callback=callback_fn)

	def callback_funcbtn_onboth(self, callback_fn):
		gpio.add_event_detect(self.funcbtn, gpio.BOTH, callback=callback_fn)


if __name__ == "__main__":
	import haconfig
	config = haconfig.Config()
	config.readConfig("/etc/hahub/hahubd.conf")

	gpioops = GPIOops()
	gpioops.setconfig(config)
	gpioops.initGPIOs()
	gpioops.hlthledon()
	time.sleep(0.25)
	gpioops.hlthledoff()
	time.sleep(0.25)
	gpioops.wstsledon()
	time.sleep(0.25)
	gpioops.wstsledoff()
	time.sleep(0.25)

	def wps_falling(btnid):
		gpio.output(gpioops.hahubstsLED1, True)
	def wps_rising(btnid):
		gpio.output(gpioops.hahubstsLED1, False)
	gpioops.callback_wpsbtn_onfalling(wps_falling)
	# gpioops.callback_wpsbtn_onrising(wps_rising)
	time.sleep(10)

	gpioops.cleanupGPIOs()
