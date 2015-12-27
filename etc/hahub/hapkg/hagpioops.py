#!/usr/bin/python

import RPi.GPIO as gpio
import time
import threading

class GPIOops:
	def __init__(self):
		self.hlthLED = 19
		self.wstsLED = 13
		self.hahubstsLED1 = 5
		self.hahubstsLED2 = 6
		self.wpsbtn = 17
		self.funcbtn = 27
		self.ledcmd = {}
		self.ledpwr = {}

	def setconfig(self, config):
		self.config = config

	def updateLEDs(self):
		# P = Persistent on/off
		# B = Blink a count number of times, then off
		while True:
			for ledID in self.ledcmd.keys():
				cat,val = self.ledcmd[ledID]
				if cat == "P":
					self.ledpwr[ledID] = val
					self.setLEDpwr(ledID,self.ledpwr[ledID])
					self.ledcmd[ledID] = ["X",0]
				if cat == "B":
					if val > 0:
						if self.ledpwr[ledID]:
							self.ledcmd[ledID] = ["B",val-1]
						self.ledpwr[ledID] = not self.ledpwr[ledID]
						self.setLEDpwr(ledID,self.ledpwr[ledID])
					else:
						self.ledcmd[ledID] = ["X",0]
				if cat == "T":
					self.ledpwr[ledID] = not self.ledpwr[ledID]
					self.setLEDpwr(ledID,self.ledpwr[ledID])
				if cat == "X":
					# nothing to do
					pass
			time.sleep(0.5)

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

		self.ledpwr[self.hlthLED] = False
		self.ledpwr[self.wstsLED] = False
		self.ledpwr[self.hahubstsLED1] = False
		self.ledpwr[self.hahubstsLED2] = False

		self.setLEDblink(self.hlthLED, 2)
		self.setLEDblink(self.hahubstsLED1, 2)
		self.setLEDblink(self.wstsLED, 2)
		self.setLEDblink(self.hahubstsLED2, 2)

		tleds = threading.Thread(target=self.updateLEDs, name="UpdateLEDs")
		tleds.daemon = True
		tleds.start()

		time.sleep(4) # give time to 

	def cleanupGPIOs(self):
		gpio.cleanup()


	def setLEDoff(self,ledID):
		self.ledcmd[ledID] = ["P",False]

	def setLEDon(self,ledID):
		self.ledcmd[ledID] = ["P",True]

	def setLEDblink(self,ledID, num):
		self.ledcmd[ledID] = ["B",num]

	def setLEDtoggle(self,ledID):
		self.ledcmd[ledID] = ["T",0]

	def setLEDpwr(self,ledID, val):
		gpio.output(ledID, val)




	def hlthledon(self):
		self.setLEDon(self.hlthLED)

	def hlthledoff(self):
		self.setLEDoff(self.hlthLED)

	def wstsledon(self):
		self.setLEDon(self.wstsLED)

	def wstsledoff(self):
		self.setLEDoff(self.wstsLED)




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
	gpioops.wstsledon()
	time.sleep(1)
	gpioops.hlthledoff()
	gpioops.wstsledoff()
	time.sleep(1)

	gpioops.setLEDblink(gpioops.hlthLED,4)
	gpioops.setLEDblink(gpioops.wstsLED,4)
	gpioops.setLEDblink(gpioops.hahubstsLED1,4)
	gpioops.setLEDblink(gpioops.hahubstsLED2,4)

	def wps_falling(btnid):
		gpio.output(gpioops.hahubstsLED1, True)
	def wps_rising(btnid):
		gpio.output(gpioops.hahubstsLED1, False)
	gpioops.callback_wpsbtn_onfalling(wps_falling)
	# gpioops.callback_wpsbtn_onrising(wps_rising)
	time.sleep(10)

	gpioops.cleanupGPIOs()
