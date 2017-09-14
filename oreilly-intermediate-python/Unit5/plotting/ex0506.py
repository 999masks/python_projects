from matplotlib import pyplot
import string

let_dic = {}
file_loc = open("constitution.txt").readlines()
for lines in file_loc:
	for letters in lines:
		if letters in string.letters:
			new_let = letters.lower()
			if not new_let in let_dic:
				let_dic[new_let]=1
			else:
				let_dic[new_let]+=1


				
#print let_dic
letters = []
counts = []
for letts,count in let_dic.items():
	letters.append((letts).strip())	 
	counts.append(count)

xlocations = range(len(counts))
#xlocations is list -> possition of bars
width = 0.5
#width of the bars
pyplot.xticks([items + width/2 for items in xlocations], letters)
#calculate where along tha x-axis the ticks for each bar should
# go. We want tick to be in center of bars
#each bar is letter
pyplot.bar(xlocations, counts, width = width)	

pyplot.xlabel("Letter")
pyplot.ylabel("Freqauency")
pyplot.title("lettes frwquency in constitution")	
	
	
	
	
	
	
	
	
#counts = ['2670', '1156', '610', '5084', '1223', '443', '1019', '2415', '2023', '53', '96', '729', '1486', '2709', '26','07', '46', '763', '2661', '2193', '842', '3723', '372', '454', '503', '96'] 
#letts =  ['2670', '1156', '610', '5084', '1223', '443', '1019', '2415', '2023', '53', '96', '729', '1486', '2709', '26','07', '46', '763', '2661', '2193', '842', '3723', '372', '454', '503', '96',]
#print letters, len(letters)
#print counts, len(counts)
pyplot.plot(counts, letters,"o-") ##### why my plot is not working?????????????????



pyplot.show()	


###########conclusion###############
#1. think about your goal before parsisng text:
#	this case we need single string why read line by line?
# why my plot is not working?????????????????