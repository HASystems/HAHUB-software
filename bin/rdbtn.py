#!/usr/bin/python

import RPi.GPIO as gpio
import signal
import sys

def cleanup(signum,frame):
	gpio.cleanup()
	sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def wps_act(btn):
	print "edge detected on WPS %d" % btn
	rdval = gpio.input(btn)
	print "value = %d" % rdval
	gpio.output(5,rdval)

def func_act(btn):
	print "edge detected on FUNC %d" % btn
	rdval = gpio.input(btn)
	print "value = %d" % rdval
	gpio.output(6,rdval)

gpio.setmode(gpio.BCM)
gpio.setup(17, gpio.IN)
gpio.setup(27, gpio.IN)

gpio.setup(5, gpio.OUT)
gpio.setup(6, gpio.OUT)

gpio.add_event_detect(17, gpio.BOTH, callback=wps_act)
gpio.add_event_detect(27, gpio.BOTH, callback=func_act)

while True:
	pass
