from Sender import *
from Receiver import *
import socket
import struct
import threading
import os

PORT = 8000

SIZE = 1024 * 2

TIME = 0.2

def main():
	print ('服务端已开启')
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', PORT))
	while True:
		data, addr = s.recvfrom(SIZE)
		MAX = struct.unpack('!i', data[len(data)-4:])[0]
		tmp = data[:len(data)-4]
		tmp = tmp.decode().split(' ')
		FILENAME = tmp[0]
		option = tmp[1]

		try:
			filesize = os.path.getsize(FILENAME)
		except BaseException as e:
			print ('文件不存在')
			s.sendto(struct.pack('!i', -1), addr)
			continue

		s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s2.bind(('', addr[1]+1))

		if option == 'lget':
			s2.settimeout(TIME)
			s2.sendto(struct.pack('!i', filesize)+ struct.pack('!i', addr[1]+1), addr)
			t = threading.Thread(target=dataSend, args=(s2, addr, FILENAME, filesize))
			t.start()
		elif option == 'lsend':
			s.sendto(struct.pack('!i', addr[1]+1), addr)
			t = threading.Thread(target=dataReceive, args=(s2, addr, FILENAME, MAX))
			t.start()
	s.close()

if __name__ == '__main__':
	main()