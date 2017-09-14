from matplotlib import pyplot

data = open("life_expectancies_usa.txt", "r").readlines()

years = []
men = []
womens = []

for data in data:
	year, man, women = data.split(",")
	years.append(year)
	men.append(man)
	womens.append(women)

print years, men, womens	
	
pyplot.plot(years, men, "bo-", label = "Men")
pyplot.plot(years, womens, "mo-", label = "Women")
pyplot.ylabel("Time")
pyplot.xlabel("Age")
pyplot.legend(loc="upper left")

pyplot.title("man, women population")

pyplot.show()	