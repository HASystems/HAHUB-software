#!/usr/bin/python

class Config:

	def __init__(self):
		self.configmap = {}

	def readConfig(self, configfile):
		self.configmap = {}
		linenum=0
		cfg = open(configfile)
		for rdline in cfg:
			line = rdline.rstrip('\n')
			linenum += 1
			if len(line) >=1:
				if line[0] != '#':
					if line.find('=') > 1:
						k,v = line.split('=')
						self.configmap[k] = v
					else:
						print "wifimon: line number " + str(linenum) + " Ignored incorrect config info -- "+line
						print "Ignored incorrect config info -- "+line
		cfg.close()

	def getConfigValue(self, k, defval):
		if k in self.configmap:
			return self.configmap[k]
		else:
			print "wifimon: Key NOT found in config info -- " + k
			return defval

	def getConfigIntValue(self, k, defval):
		return int(self.getConfigValue(k,defval))

	def getConfigFloatValue(self, k, defval):
		return float(self.getConfigValue(k,defval))

	def setConfigValue(self, k, val):
		self.configmap[k] = val


if __name__ == "__main__":
	config = Config()
	config.readConfig("/etc/hahub/hahubd.conf")
	print config.getConfigValue("RES_BCASTPORT",1)

