#!/usr/bin/python

import RPi.GPIO as gpio
import time
import threading

class GPIOops:
	def __init__(self):
		self.hlthLED = 19
		self.wstsLED = 13
		self.stsLED1 = 5
		self.stsLED2 = 6
		self.wpsbtn = 17
		self.funcbtn = 27
		self.ledcmd = {}
		self.ledpwr = {}

	def updateLEDs(self):
		# P = Persistent on/off
		# B = Blink a count number of times, then off
		# T = Toggle (blink) indefinitely till another command
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

	def setLEDpwr(self, ledID, val):
		gpio.output(ledID, val)


	############################################################################################################
	# This is the core API for external use 
	# To use this module do the following
	#
	# import hagpioops
	# ...
	# gpioopsObj = hagpioops.GPIOops()
	# gpioopsObj.setconfig(configObj)  # use the haconfig module to create this configObj
	# gpioopsObj.initGPIOs()
	# ...
	# # ... and now use the other API functions of this module to perform the operations
	#
	############################################################################################################
	# Configuration Information
	#   Key					Default value					Type		Comment
	#	----------------	----------------				--------	-------------------------
	#	HLTHLED				19								Integer		GPIO # of Health LED
	#	WSTSLED				13								Integer		GPIO # of WiFi status LED
	#	HAHUBSTSLED1		5								Integer		GPIO # of Status 1 LED
	#	HAHUBSTSLED2		6								Integer		GPIO # of Status 2 LED
	#	WPS_BTN				17								Integer		GPIO # of WPS button
	#	FUNC_BTN			27								Integer		GPIO # of FUNC button
	#
	############################################################################################################

	def setconfig(self, config):
		self.config = config

	def initGPIOs(self):
		self.hlthLED = self.config.getConfigIntValue("HLTHLED",19)
		self.wstsLED = self.config.getConfigIntValue("WSTSLED",13)
		self.stsLED1 = self.config.getConfigIntValue("HAHUBSTSLED1",5)
		self.stsLED2 = self.config.getConfigIntValue("HAHUBSTSLED2",6)

		self.wpsbtn = self.config.getConfigIntValue("WPS_BTN",17)
		self.funcbtn = self.config.getConfigIntValue("FUNC_BTN",27)

		gpio.setwarnings(False)
		gpio.setmode(gpio.BCM)

		gpio.setup(self.hlthLED, gpio.OUT)
		gpio.setup(self.wstsLED, gpio.OUT)
		gpio.setup(self.stsLED1, gpio.OUT)
		gpio.setup(self.stsLED2, gpio.OUT)

		gpio.setup(self.wpsbtn, gpio.IN)
		gpio.setup(self.funcbtn, gpio.IN)

		self.ledpwr[self.hlthLED] = False
		self.ledpwr[self.wstsLED] = False
		self.ledpwr[self.stsLED1] = False
		self.ledpwr[self.stsLED2] = False

		self.setLEDblink(self.hlthLED, 4)
		self.setLEDblink(self.stsLED1, 4)
		self.setLEDblink(self.wstsLED, 4)
		self.setLEDblink(self.stsLED2, 4)

		tleds = threading.Thread(target=self.updateLEDs, name="UpdateLEDs")
		tleds.daemon = True
		tleds.start()

		# time.sleep(4) # give time to complete the blinking

	#
	# use this in callbacks to freeup the GPIO system from your app
	#
	def cleanupGPIOs(self):
		gpio.cleanup()

	#########################################################################################
	# This is API for LED operations if the LEDs IDs are known to the calling application
	#########################################################################################

	def setLEDon(self,ledID):
		self.ledcmd[ledID] = ["P",True]

	def setLEDoff(self,ledID):
		self.ledcmd[ledID] = ["P",False]

	def setLEDblink(self,ledID, num):
		self.ledcmd[ledID] = ["B",num]

	def setLEDtoggle(self,ledID):
		self.ledcmd[ledID] = ["T",0]


	#########################################################################################
	# This API abstracts the LED IDs through appropriate function names
	#########################################################################################

	def hlthledon(self):
		self.setLEDon(self.hlthLED)

	def hlthledoff(self):
		self.setLEDoff(self.hlthLED)

	def hlthledblink(self,num):
		self.setLEDblink(self.hlthLED, num)

	def hlthledtoggle(self):
		self.setLEDtoggle(self.hlthLED)



	def wstsledon(self):
		self.setLEDon(self.wstsLED)

	def wstsledoff(self):
		self.setLEDoff(self.wstsLED)

	def wstsledblink(self, num):
		self.setLEDblink(self.wstsLED, num)

	def wstsledtoggle(self):
		self.setLEDtoggle(self.wstsLED)



	def stsLED1ledon(self):
		self.setLEDon(self.stsLED1)

	def stsLED1ledoff(self):
		self.setLEDoff(self.stsLED1)

	def stsLED1ledblink(self, num):
		self.setLEDblink(self.stsLED1, num)

	def stsLED1ledtoggle(self):
		self.setLEDtoggle(self.stsLED1)



	def stsLED2ledon(self):
		self.setLEDon(self.stsLED2)

	def stsLED2ledoff(self):
		self.setLEDoff(self.stsLED2)

	def stsLED2ledblink(self, num):
		self.setLEDblink(self.stsLED2, num)

	def stsLED2ledtoggle(self):
		self.setLEDtoggle(self.stsLED2)



	#########################################################################################
	# This API is for registering callback functions for the two buttons on HAHUB board
	#########################################################################################

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
	gpioops.setLEDblink(gpioops.stsLED1,4)
	gpioops.setLEDblink(gpioops.stsLED2,4)

	def wps_falling(btnid):
		gpio.output(gpioops.stsLED1, True)
	def wps_rising(btnid):
		gpio.output(gpioops.stsLED1, False)
	gpioops.callback_wpsbtn_onfalling(wps_falling)
	# gpioops.callback_wpsbtn_onrising(wps_rising)
	time.sleep(10)

	gpioops.cleanupGPIOs()
	print "Exiting ..."
