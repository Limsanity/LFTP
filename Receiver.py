import socket
import struct
import threading
import time
import sys
from Packet import *

SIZE = 1024 * 2
BUFFERSIZE = 128
p = 0

def writeData(f, SEQ, bufferData):
	bufferData.sort(key=lambda x:x.getSeq(),reverse=False)
	count = 0
	for j in range(len(bufferData)):
		if bufferData[j].getSeq() == SEQ:
			count = count + 1
			f.write(bufferData[j].getContent())
			SEQ = SEQ + 1
	bufferData = bufferData[count:]
	return bufferData, SEQ

def receivePakcet(s):
	data = s.recvfrom(SIZE)[0]
	windowSize = struct.unpack('!i', data[0:4])[0]
	seq = struct.unpack('!i', data[4:8])[0]
	data = data[8:]
	return data, seq, windowSize
	
def handleProcess(total):
	global p

	t0 = time.clock()
	while True:
		process = (p*1000/(total))*100
		if p*1000 - total >= 0:
			tmp = '[' + '#' * 49 + '-'*(0) + ']' + ' ' + '%.2f' % 100 + '%' + '\r'
			sys.stdout.write(tmp)
			sys.stdout.flush()
			break
		else:
			i = round(process/2)
			tmp = '[' + '#' * i + '-'*(49-i) + ']' + ' ' + '%.2f' % process + '%' + '\r'
		sys.stdout.write(tmp)
		sys.stdout.flush()
		time.sleep(0.1)
	print("")
	t1 = time.clock()
	print ('结束')
	print ('使用时间: ', (t1-t0)/60, '分钟')
	print ('传输速度： ', (total/(1024*1024))/(t1-t0), 'MB/s')


def dataReceive(s, addr, filename, filesize):
	global p
	MAX = filesize
	bufferData = []
	save = set([])
	SEQ = 0

	t = threading.Thread(target=handleProcess, args=(filesize,))
	t.start()

	i = 0
	with open(filename, 'wb') as f:
		total = MAX
		while True:
			if MAX <= 0:
				break
			data, seq, windowSize = receivePakcet(s)
			# 判断是否已经接收该包
			if not seq in save:
				packet = Packet(seq, data)
				bufferData.append(packet)
				save.add(seq)
				i = i + 1
				p = p + 1
				MAX = MAX - 1000
			s.sendto(struct.pack('!i', BUFFERSIZE-len(bufferData)) + struct.pack('!i', seq), addr)

			bufferData, SEQ =  writeData(f, SEQ, bufferData)

		

	s.close()