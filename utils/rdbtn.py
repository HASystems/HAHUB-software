#!/usr/bin/python

import sys

# First add the path of the hahub libraries so they can be imported below
(sys.path).append('/usr/local/lib/hahub')

import RPi.GPIO as gpio
import syslog
import signal
import haconfig

syslog.openlog("rdbtn",0,syslog.LOG_LOCAL0)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))

config = haconfig.Config()
config.readConfig("/etc/hahub/hahubd.conf")
wps_btn = config.getConfigIntValue("WPS_BTN",17)
func_btn = config.getConfigIntValue("FUNC_BTN",27)

ind1_led = config.getConfigIntValue("HAHUBSTSLED1",5)
ind2_led = config.getConfigIntValue("HAHUBSTSLED2",6)

def cleanup(signum,frame):
	gpio.cleanup()
	sys.exit(0)
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def wps_act(btn):
	print "edge detected on WPS %d" % btn
	rdval = gpio.input(btn)
	print "value = %d" % rdval
	gpio.output(ind1_led,rdval)

def func_act(btn):
	print "edge detected on FUNC %d" % btn
	rdval = gpio.input(btn)
	print "value = %d" % rdval
	gpio.output(ind2_led,rdval)

gpio.setmode(gpio.BCM)
gpio.setup(wps_btn, gpio.IN)
gpio.setup(func_btn, gpio.IN)

gpio.setup(ind1_led, gpio.OUT)
gpio.setup(ind2_led, gpio.OUT)

gpio.add_event_detect(wps_btn, gpio.BOTH, callback=wps_act)
gpio.add_event_detect(func_btn, gpio.BOTH, callback=func_act)

while True:
	pass
