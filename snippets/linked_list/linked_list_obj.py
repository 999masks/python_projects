class my_linked_list:
	class _Node:
		__slot__ = "_element", "_next"

		def __init__(self, element, next):
			self._element = element  # data holder
			self._next = next  # will be referiong next head

	def __init__(self):
		self._head = None
		self._size = 0

	def _is_empty(self):
		return self._size == 0

	def pop(self):
		if self._is_empty:
			raise Error("Empty list")
		answer = self._head._element
		self._head = self._head._next
		self._size -= 1
		return answer

	def push(self, new_node):
		self._head = self._Node(new_node, self._head)
		self._size += 1

	def _len(self):
		return self._size

	def top(self):
		return self._head_element

my = my_linked_list()
my.push("a")
my.push("b")