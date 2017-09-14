import os
from bs4 import BeautifulSoup
from urllib import request, parse

base_url = "https://apod.nasa.gov/apod/archivepix.html"
download_directory = "Mail_ru_images"
to_visit = set((base_url,))
visited_links = set()

while to_visit:
# 1. pick a link to visit
# 2. visit that link
# 3. store visited link
# 4. from that page extract all links and pictures
	current_link = to_visit.pop()
	print ("Current page", current_link)	
	visited_links.add(current_link)
	web_page_content = request.urlopen(current_link).read()
	#print (web_page_content)
	links = BeautifulSoup(web_page_content, "html.parser").findAll("a")
	
	
	for link in links:
		abs_link = parse.urljoin(current_link, link["href"])		
		if abs_link not in visited_links:
			to_visit.add(abs_link)
		else:
			print (("%s this page already in list to visit")%abs_link) 
		
		
		
	for image in BeautifulSoup(web_page_content, "html.parser").findAll("img"):		
		abs_img_link = parse.urljoin(current_link, image["src"])
		print ("Downloading images from %s page" % abs_img_link)
		image_name = abs_img_link.split("/")[-1]
		print ("image_name", image_name)
		request.urlretrieve(abs_img_link, os.path.join(download_directory, image_name))	
		
		
	
#print ("to be visited", to_visit)
#print ("already visited", visited_links)

#########################################
#conclusions:
#1. if set has the same item that you want to add, it will not relplace with existing one.
#		it will do nothing...
#2. think deeply while you do looping, LETS say does nxt loop should run nested or NOT????