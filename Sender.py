import socket
import struct
import threading
import sys
import time
from Packet import *

SIZE = 1024 * 2

TIME = 0.3

class MyThread(threading.Thread):

    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def slideWindow(bufferData, state):
	count = 0
	for i in range(len(bufferData)):
		if state[bufferData[i].getSeq()] == 2:
			count = count + 1
		else:
			break
	bufferData = bufferData[count:]
	return bufferData

def sendPacket(s, addr, packet, WINDOW_SIZE):
	seq = packet.getSeq()
	content = packet.getContent()
	s.sendto(struct.pack('!i', WINDOW_SIZE) + struct.pack('!i', seq) + content, addr)

def receiveAnswer(s,WINDOW_SIZE):
	print('窗口大小： ', WINDOW_SIZE)
	try:
		data = s.recvfrom(SIZE)[0]
		windowSize = struct.unpack('!i', data[0:4])[0]
		seq = struct.unpack('!i', data[4:8])[0]
		return windowSize, seq
	except BaseException as e:
		print (e)
		return None, None

def dataSend(s, addr, filename, filesize):
	FINISH = False
	bufferData = []
	state = []
	SEQ = 0
	RESEND = 0
	WINDOW_SIZE = 1
	ssthread = 64
	countLost = 0

	t0 = time.clock()
	
	with open(filename, 'rb') as f:
		while True:
			if FINISH and len(bufferData)==0:
				print ('重传率： ', countLost/(filesize) * 100000, '%')
				break
			
			if WINDOW_SIZE == 0:
				WINDOW_SIZE = WINDOW_SIZE + 1
			# r for range
			r = 0
			if WINDOW_SIZE-len(bufferData) > 0:
				for i in range(WINDOW_SIZE-len(bufferData)):
					chunk = f.read(1000)
					if not chunk:
						FINISH = True
						break
					packet = Packet(SEQ, chunk)
					bufferData.append(packet)
					state.append(0)
					SEQ = SEQ + 1
				r = len(bufferData)
			else:
				r = WINDOW_SIZE

			# count for numbers of packet need to be sent
			count = 0
			for i in range(r):
				if state[bufferData[i].getSeq()] == 0:
					sendPacket(s, addr, bufferData[i], WINDOW_SIZE)
					state[bufferData[i].getSeq()] = 1
					count = count + 1
			
			li = []
			for i in range(count):
				t = MyThread(receiveAnswer,args=(s,WINDOW_SIZE))
				li.append(t)
				t.start()

			tag = False
			for t in li:
				t.join()
				windowSize, seq = t.get_result()
				if windowSize is None and seq is None:
					ssthread = WINDOW_SIZE // 2
					WINDOW_SIZE = 1
					RESEND = RESEND + 1
					countLost = countLost + 1
				else:
					state[seq] = 2
					if windowSize < WINDOW_SIZE:
						WINDOW_SIZE = windowSize
					else:
						if ssthread > WINDOW_SIZE:
							WINDOW_SIZE  = WINDOW_SIZE + 1
							tag = True
			if (not tag) and RESEND==0:
				WINDOW_SIZE = WINDOW_SIZE + 1
			RESEND = 0

			for i in range(r):
				if state[bufferData[i].getSeq()] == 1:
					state[bufferData[i].getSeq()] = 0

			bufferData = slideWindow(bufferData, state)

		t1 = time.clock()
		print ('结束')
		print ('使用时间: ', (t1-t0)/60, '分钟')
		print ('传输速度： ', (filesize/(1024*1024))/(t1-t0), 'MB/s')
		s.close()