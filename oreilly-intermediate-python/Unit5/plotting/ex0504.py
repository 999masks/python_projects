from matplotlib import pyplot

# doc = open("world_population.txt", "r")

# text_data = doc.readlines()

# date = []
# population = []

# for item in text_data:
	# date.append(item.split()[0])
	# population.append(item.split()[1])
	
# pyplot.plot(x_val, y_val, "o-")
# pyplot.xlabel("year")
# pyplot.ylabel("population")
# pyplot.title("world population")
# pyplot.show()	 


#nicer version

data = open("world_population.txt", "r").readlines()

dates = []
populations = []

for points in data:
	print "points", points, type(points)
	date, population = points.split()
	dates.append(str(date))
	populations.append(str(population)) # testing str can be plotted or not
	
pyplot.plot(dates, populations, "o-")
pyplot.xlabel("Year")
pyplot.ylabel("Populatation")
pyplot.title("Word populatation for 40 years")

pyplot.show()
	
############Conclusion#######################
#1. dont forget parentensis after method EX. readlines -> ()
#2. for this case no need to split by whitespace, split parameter can be empty
#3. when read data from file, you can use readlines method straight after open function