#!/usr/bin/python

import threading
import time

class Logger:
	def __init__(self):
		# default values if configlogger() is not called
		self.loglevelconf="/etc/hahub/loglevel.conf"
		self.logfiledir="/var/log/hahub"
		self.logfilebase="hahub"
		self.oldsevconf=3
		self.lk = threading.Lock()

	def configlogger(self, conffile, dir, base):
		self.loglevelconf = conffile
		self.logfiledir = dir
		self.logfilebase = base

	def gettm(self):
		now = time.ctime()
		parsedtm = time.strptime(now)
		return time.strftime("%Y-%m-%d %H:%M:%S",parsedtm)

	def setsevconf(self, lvl):
		f = open(self.loglevelconf,'w')
		f.write("%d" % lvl)
		f.close()

	def getsevconf(self):
		f = open(self.loglevelconf,'r')
		loglevel = f.readline()
		f.close()
		return int(loglevel)

	def log(self, sev, logstr):
		self.lk.acquire(True)
		logfilename = self.logfiledir+"/"+self.logfilebase+".log"
		sevconf = self.getsevconf()
		if sevconf != self.oldsevconf:
			confmsg = "Logging level changed from " + "%d"%self.oldsevconf + " to " + "%d"%sevconf
			self.oldsevconf = sevconf
			logfile = open(logfilename,"a")
			logfile.write(self.gettm() + " " + confmsg + "\n")
			logfile.close()
		if sev >= sevconf:
			logfile = open(logfilename,"a")
			logfile.write(self.gettm() + " " + logstr + "\n")
			logfile.close()
		self.lk.release()


if __name__ == "__main__":
	logger = Logger()
	logger.setsevconf(1)
	logger.log(3,"Test warniong level message")
	logger.log(5,"Test critical level message")
	logger.log(1,"Test informational level message")
	logger.setsevconf(3)
	logger.log(3,"Test warniong level message")
	logger.log(5,"Test critical level message")
	logger.log(1,"Test informational level message")
