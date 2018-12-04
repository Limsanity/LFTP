import socket
import struct
import threading
import sys
import os
from Sender import *
from Receiver import *

TIME = 0.2

def main():
	PORT = 8000
	FILENAME = ''
	IP = ''
	SIZE = 1024 * 2

	option = str(sys.argv[2])
	IP = str(sys.argv[3])
	FILENAME = str(sys.argv[4])

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	if option == 'lget':
		s.sendto(str.encode(FILENAME + ' ' + option) + struct.pack('!i', 0), (IP, PORT))
		data = s.recvfrom(SIZE)[0]
		MAX = struct.unpack('!i', data[0:4])[0]
		if MAX == -1:
			print ('文件不存在')
			return
		PORT = struct.unpack('!i', data[4:8])[0]
		dataReceive(s, (IP, PORT), FILENAME, MAX)
	else:
		print (IP, PORT)
		try:
			MAX = os.path.getsize(FILENAME)
		except BaseException as e:
			print ('文件不存在')
			return
		s.settimeout(TIME)
		s.sendto(str.encode(FILENAME + ' ' + option) + struct.pack('!i', MAX), (IP, PORT))
		data = s.recvfrom(SIZE)[0]
		PORT = struct.unpack('!i', data[0:4])[0]
		dataSend(s, (IP, PORT), FILENAME, MAX)

if __name__ == '__main__':
	main()