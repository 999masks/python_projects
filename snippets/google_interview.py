my_dic = {1:"house", 2:"key", 3:"list", 4:"pass"}
input_string = "databringpasstounityoumaylistwantedhomehouseuseyourown"


# for word in my_dic.itervalues():
# 	if word in input_string:
# 		input_string = input_string[:len(word)]
# 		sentence = sentence + word + " "
# print sentence

# # for i in my_dic.itervalues():
# 	print i


#my_dic = {1: "use", 2: "you", 3: "own"}
new_sentennce = ""
new_word = ""

for word in my_dic.itervalues():
	if word in input_string:
		intit_pos = 0
		start_ind = input_string.find(word[0])
		print start_ind
		for letter in word[1:]:
			start_ind = start_ind + 1
			if letter == input_string[start_ind]:
				continue
			else:
				start_ind = input_string[start_ind:].find(word[0])
		end_ind = start_ind + len(word)-1
		print "end_int", end_ind
		new_sentennce = new_sentennce + word + " "
		input_string = input_string[:start_ind] + input_string[end_ind:]


print "new sentence", new_sentennce
print "input string", input_string

			#
			#
			# end_index = input_string.index(word[-1])
			# else:
			# 	start_ind = input_string[start_ind:].find(word[0])
			#
			# 	new_word = ""
			# 	break


			# new_sentennce = new_sentennce + letter


class my():

	version = "version"
	def _int__(self, name):
		self.name = name
		self.version = "version"

you = my