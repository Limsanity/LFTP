class Packet:
	def __init__(self, seq, content):
		self.seq = seq
		self.content = content

	def getSeq(self):
		return self.seq

	def getContent(self):
		return self.content