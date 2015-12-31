#!/usr/bin/python

class Config:

	####################################################################################
	# Utility for maintaining the config information of multiple modules in one place and 
	# sharing it among various HAHUB mudues via a configuration object
	# 
	# Very simple file format:
	#     * No leading spces or tabs are allowed
	#     * Comment line - starts with a # charater, the entire line is ignored
	#     * Blank (empty) lines are allowed to help format the information visually into groups
	#     * key=value pairs, one per line. The characters in the lione before the '=' character
	#         constitute the key name, all text after constitutes its value.
	# Example:
	# # this is a comment
	# NUMBER_OF_THREADS=10
	# DELAY=0.25
	# LOG_FILE=/var/log/hahub/hahubd.log
	# # Another comment
	# 
	#
	# API Functions --
	#
	# readconfig() 
	#         Takes as a parameter a config filename. As of current implementation it should be 
	#         called only once for one config object. Easy to change to support multiple calls 
	#         each adding/overwriting config parameter values.
	#
	# getConfigValue(key, default_value) - returns a string value for the key.
	#         default_value must be a string. It is returned if key name is not found.
	# 
	# getConfigInt(key, default_value) - returns an integer value for the key.
	#         default_value must be an integer. It is returned if key name is not found.
	# 
	# getConfigFloat(key, default_value) - returns a floating point value for the key.
	#         default_value must be a floating point number. It is returned if key name is not found.
	# 
	# setConfigValue(key, value) - makes an entry of this pair in the config object.
	#         Does NOT make this entry in the config file. Just a maeans to share
	#         this new pair with other modules. This function is not used often.
	####################################################################################

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

