class deque:

	def __init__(self):
		self.dequeue = list()

	def add_rear(self, item):
		self.dequeue.append(item)

	def remove_rear(self):
		if self.size() > 0:
			return self.dequeue.pop()

	def add_front(self, item):
		self.dequeue.insert(0, item)

	def remove_front(self):
		if self.size() > 0:
			return self.dequeue.pop(0)

	def size(self):
		return len(self.dequeue)

	def isempty(self):
		return self.size() == 0


my = deque()
