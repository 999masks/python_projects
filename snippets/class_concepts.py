#
#
# class person(object):
# 	def __init__(self, name):
# 		self.name = name
# 		self.__default_name = "Peter"
# 		self._default_race = "American"
# 		self.__default_age = "50"
#
# 	def isworker(self):
# 		return True
#
#
#
# class worker(person):
#
# 	def isworker(self):
# 		return False
#
#
#
# Ashot = person("Ashot")
# print Ashot.isworker()
# print Ashot._default_race
# Ashot._default_race = "Armenian"
# print Ashot._default_race
#
# Karen = worker("Karen")
# print Karen.isworker()

class person(object):

	def __init__(self, name):
		self.name = name
		self.default_age = "20"
		self._default_color = "Black"
		self.__default_location = "USA"

	def get_default_location_own(self):
		return self.__default_location

	def set_default_location(self, string):
		self.__default_location = string

	def isworker(self):
		return False


class worker(person):
	def isworker(self):
		return True


Karen = person("Karen")
print Karen.name
print Karen.isworker()

Ashot = worker("Ashot")
print "ashot", Ashot.get_default_location_own()

Ashot.set_default_location("Gjumri")
print "ashot loc changed", Ashot.get_default_location_own()
#Ashot.set_default_location("Yas")
print "yas"

Ashot.isworker()
print Ashot.default_age
print Ashot._default_color


class modifier(person):
	def get_default_location(self):
		return person.get_default_location_own()


print "KAren", Karen.get_default_location_own()

Tigran = modifier("Tigran")
Tigran.get_default_location()

