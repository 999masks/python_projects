class dequeue:

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




def is_polindrome(word):
	new_deque = dequeue()
	stop = False

	for letters in word:
		new_deque.add_front(letters.lower())

	while not new_deque.isempty() and not stop:
		if new_deque.size() > 1:  # if the size is 1 - cannot pop on both sides !!!
			if new_deque.remove_front() != new_deque.remove_rear():
				stop = True
			else:
				stop = False
		else:
			break

	# while not new_deque.isempty():
	# 	if new_deque.size() > 1:  # if the size is 1 - cannot pop on both sides !!!
	# 		if new_deque.remove_front() != new_deque.remove_rear():
	# 			return "not"
	#
	# 	if new_deque.size() == 1 or new_deque.size() == 0 :
	# 		return "yes"
	# return "yers"

	# if not stop:
	# 	return "Yes polyndrome"
	# else:
	# 	return "Not poly"


def is_polindrome_book(word):  # book version
	new_deque = dequeue()
	keep_going = True

	for letters in word:
		new_deque.add_front(letters.lower())

	while new_deque.size() > 1 and keep_going:
		if new_deque.remove_front() != new_deque.remove_rear():
			keep_going = False

	return keep_going


print  is_polindrome_book("1898")