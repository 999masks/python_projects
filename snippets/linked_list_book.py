class LinkedStack:
	class _Node:
		__slots__ = "_elements", "_next"

		def __init__(self, element, next):
			self._element = element
			self._next = next

	def __init__(self):
		self._head = None
		self._size = 0

	def __len__(self):
		return self._size

	def is_empty(self):
		return self._size == 0

	def push(self, e):
		self._head = self._Node(e, self._head)
		self._size += 1
		#print "next ->", self._next


	def top(self):
		if self.is_empty():
			raise Empty("Stack is empty")
		return self._head._element

	def pop(self):

		if self.is_empty():
			raise ("Stack is empty")
		answer = self._head._element
		self._head = self._head._enxt
		self._size -= 1
		return  answer

# my = LinkedStack()
#
# my.push("a")
# my.push("b")
# print "top", my.top()

class Node:
	def __init__(self, initdata):
		self.data = initdata
		self.next = None

	def getData(self):
		return self.data

	def getNext(self):
		return self.next

	def setData(self, newdata):
		self.data = newdata

	def setNext(self, newnext):
		self.next = newnext


class UnorderedList():

	def __init__(self):
		self.head = None
		self.last_node = None

	def isEmpty(self):
		return self.head == None

	def add(self, item):
		temp = Node(item)
		temp.setNext(self.head)
		self.head = temp
		if self.size() == 1:
			self.last_node = self.head

	def size(self):
		current = self.head
		count = 0
		while current != None:
			count = count + 1
			# print type(current)
			current = current.getNext()
		return count

	def search(self, item):
		current = self.head
		found = False
		while current != None and not found:
			if current.getData() == item:
				found = True
			else:
				current = current.getNext()

		return found

	def remove(self, item):
		current = self.head
		previous = None
		found = False
		while not found:
			if current.getData() == item:
				found = True
			else:
				previous = current
				current = current.getNext()

		if previous == None:
			self.head = current.getNext()
		else:
			previous.setNext(current.getNext())

	def append_v2(self, item):
		counter = self.size()
		#print counter
		tmp_node = Node(item)
		if counter > 0:
			current_node = self.head
			while counter > 1:
				current_node = current_node.getNext()
				counter -= 1
			current_node.setNext(tmp_node)
		else:
			self.head = tmp_node

	def pop(self):
		if self.head != None:
			tmp_list = self.head
			self.head = tmp_list.getNext()
			return tmp_list.getData()

	def append_v3(self, item):
		tmp_node = Node(item)
		if self.size() > 0:
			self.last_node.setNext(tmp_node)
		else:
			self.add(item)

mylist = UnorderedList()
# mylist.add("a")
# mylist.add("b")
mylist.append_v3("C")
#print mylist.size()
print mylist.pop()
print mylist.pop()
print mylist.pop()
print mylist.pop()