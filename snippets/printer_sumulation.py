from pythonds.basic.queue import Queue

import random


class Printer:
	def __init__(self, ppm):
		self.pagerate = ppm
		self.currentTask = None
		self.timeRemaining = 0

	def tick(self):
		if self.currentTask != None:
			self.timeRemaining = self.timeRemaining - 1
			if self.timeRemaining <= 0:
				self.currentTask = None

	def busy(self):
		if self.currentTask != None:
			return True
		else:
			return False

	def startNext(self, newtask):
		self.currentTask = newtask
		self.timeRemaining = newtask.getPages() * 60 / self.pagerate


class Task:
	def __init__(self, time):
		self.timestamp = time
		self.pages = random.randrange(1, 21)

	def getStamp(self):
		return self.timestamp

	def getPages(self):
		return self.pages

	def waitTime(self, currenttime):
		return currenttime - self.timestamp


def simulation(numSeconds, pagesPerMinute, students):
	labprinter = Printer(pagesPerMinute)
	printQueue = Queue()
	waitingtimes = []

	for currentSecond in range(numSeconds):

		if newPrintTask(students):
			task = Task(currentSecond)
			printQueue.enqueue(task)

		if (not labprinter.busy()) and (not printQueue.isEmpty()):
			nexttask = printQueue.dequeue()

			waitingtimes.append(nexttask.waitTime(currentSecond))
			labprinter.startNext(nexttask)

		labprinter.tick()

	averageWait = sum(waitingtimes) / len(waitingtimes)
	print("Average Wait %6.2f secs %3d tasks remaining." % (averageWait, printQueue.size()))


def newPrintTask(students):
	if students > 0:
		required_comple_time = 3600 / (students * 2)
		num = random.randrange(1, required_comple_time + 1)
		if num == required_comple_time:
			return True
		else:
			return False
	else: return "wrong imput"

for i in range(10):
	simulation(3600, 5, 20)

# this program is based on the probibilty that in 3600 chance at least on time neWprinttask will hit
# 180 and return true otherwise program will throw 0 division error
# oany hit time the queue gets created if num sec decerease to 230 sometime it will throw error
