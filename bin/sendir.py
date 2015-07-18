import socket
import sys
import time


s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
srvr_addr = "/var/run/lirc/lircd"
print "Connecting ..."
try:
	s.connect(srvr_addr)
except socket.error, msg:
	print msg
	sys.exit(1)

try:
	cmd = "SEND_ONCE RX-V675 KEY_VOLUMEUP\n"
	print "Sendiong cmd ..."
	s.sendall(cmd)
	time.sleep(1)
	data = s.recv(1024)
	print 'Received "%s"' % data

finally:
	print "Closing socket ..."
	s.close
