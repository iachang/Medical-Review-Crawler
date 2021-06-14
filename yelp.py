import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import csv
import time 

urls = ['https://www.yelp.com/search?find_desc=plastic%20surgery&find_loc=Los%20Angeles%2C%20CA&ns=1&start=', 
'https://www.yelp.com/search?find_desc=plastic%20surgery&find_near=new-york-city-new-york-14&start=', 
'https://www.yelp.com/search?find_desc=plastic%20surgery&find_loc=Chicago%2C%20IL&start=', 
'https://www.yelp.com/search?find_desc=plastic%20surgery&find_loc=miami&start=', 
'https://www.yelp.com/search?find_desc=plastic%20surgery&find_loc=Houston&start=', 
'https://www.yelp.com/search?find_desc=plastic%20surgery&find_loc=Philadelphia%2C%20PA&start=']

max_results = 20

# Initialize CSV File
csvfile = open('yelp.csv', 'w')
csvwriter = csv.writer(csvfile)
locs = ['Los Angeles', 'New York', 'Chicago', 'Miami','Houston', 'Philadelphia']
fields = ['Location', 'Doctor', 'Review Stars', 'Review Text']
csvwriter.writerow(fields)

# Scan through all of our provided URLs
for url_id in range(len(urls)):
	url = urls[url_id]
	location = locs[url_id]

	for page_num in range(0, max_results, 10):
		# Create links that retrieve additional query results for that same search term
		URL = url + str(page_num)
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, 'html.parser')

		results = soup.find_all("h4", {"class": "css-1l5lt1i"})

		review_links = []

		for result in results:
			# Within all the search results for that page
			# Fetch all doctors
			company_elem = result.find('a', class_='css-166la90')
			if not company_elem:
				continue
			doctor = company_elem.text.strip()
			
			# Create link for doctor's review
			link = "https://yelp.com" + company_elem['href']
			review_links.append(link)
			print(doctor + ": " + link)

			# Acccess doctor's review
			link_page = requests.get(link)
			link_soup = BeautifulSoup(link_page.content, 'html.parser')

			num_pages = 0

			# Parse doctor's total pages of reviews
			nav_filter = link_soup.find_all("div", {"aria-label": "Pagination navigation"})
			for i in nav_filter:
				total_review_pages = i.find("span", class_=" css-e81eai")
				if not total_review_pages:
					continue
				num_pages = int(total_review_pages.text.strip().split(" of ")[1])
				print(num_pages)
				break

			# Iterate through all of the doctor's pages of reviews
			for page_iter in range(0, num_pages * 10, 10):
				# Load the each doctor's review page
				ind_review_link = link + "&start=" + str(page_iter)
				#print(ind_review_link)
				ind_review_page = requests.get(ind_review_link)
				ind_review_soup = BeautifulSoup(ind_review_page.content, 'html.parser')
				ind_review_filter = ind_review_soup.find_all("div", {"class": "review__373c0__13kpL"})

				# Iterate through all reviews on that current page
				for review_filter in ind_review_filter:
					# Parse the review number of stars and text
					review_stars = review_filter.find("div", class_="i-stars__373c0__1T6rz")
					review_text = review_filter.find("span", class_=" raw__373c0__3rcx7")

					#print("\n")
					#print(review_stars['aria-label'])
					#print(review_filter.text.strip())
					#print("\n")
					csvwriter.writerow([location, doctor, review_stars['aria-label'], review_filter.text.strip()])


	print("\n === Next URL === \n")
			
