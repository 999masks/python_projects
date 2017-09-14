from urllib import request, parse
#import urllib # urlopen as url_open
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import os 

base_url = "https://learncodethehardway.org/more-python-book/"
download_directory = "Interactive_python_lesson"

init_page="ex.html"

for i in range(60):
	full_url = base_url+"ex%d.html"%i	
	web_obj = request.urlopen(full_url).read()
	save_web_page = open("ex%d.html"%i, "wb")
	save_web_page.write(web_obj)
	
	




# for raw_link in links:
	# link = urljoin(base_url, raw_link["href"])
	# print ("following link ",link)
	# new_content = request.urlopen(link).read()
	# for raw_img_link in BeautifulSoup(new_content, "html.parser").findAll("img"):
		# image_link = urljoin(link, raw_img_link["src"])		
		# file_info = request.urlopen(image_link).info()
		# #print (file_info)
		# file_size = file_info["Content-Length"]
		# image_name = image_link.split("/")[-1]
		# #print ("image_size", file_size)
		# if int(file_size) > 20000:
			# print ("Downloading pictures...",image_name)
			# request.urlretrieve(image_link, os.path.join(download_directory, image_name))
	
	



