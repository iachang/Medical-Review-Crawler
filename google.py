import requests
from bs4 import BeautifulSoup
from parse import parse
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import csv
import time 

# Helper function to simulate scrolls for a certain number of desired results
def sim_scroll(browser, scroll_div, results):
	# Execute it two times to start the Google refresh review link
	browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scroll_div)
	time.sleep(1)
	browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scroll_div)
	time.sleep(1)

	for _ in range(0, results, 10):
		browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scroll_div)
		time.sleep(1)

	# Finish loading all the reviews
	time.sleep(5)

# Initialize CSV file
csvfile = open('google.csv', 'w')
csvwriter = csv.writer(csvfile)
locs = ['Los Angeles', 'New York', 'Chiacgo', 'Miami', 'Houston', 'Philadelphia']
fields = ['Location', 'Doctor', 'Review Stars', 'Review Text']
csvwriter.writerow(fields)

urls = ['https://www.google.com/maps/search/plastic+surgery+in+los+angeles/@34.0435847,-118.466442,12z/data=!3m1!4b1',
'https://www.google.com/maps/search/plastic+surgery+in+new+york/@40.7107897,-74.1539458,10z/data=!3m1!4b1',
'https://www.google.com/maps/search/plastic+surgery+in+chicago/@41.9140251,-87.8670071,11z/data=!3m1!4b1',
'https://www.google.com/maps/search/plastic+surgery+in+miami/@25.7530049,-80.3430056,11.73z',
'https://www.google.com/maps/search/plastic+surgery+in+houston/@29.7893914,-95.6394165,10z/data=!3m1!4b1',
'https://www.google.com/maps/search/plastic+surgery+in+philadelphia/@39.9964287,-75.2603094,11z/data=!3m1!4b1']

max_results = 10

for url_id in range(len(urls)):
	url = urls[url_id]
	location = locs[url_id]
	for page_num in range(0, max_results, 10):
		#URL = url + str(page_num)

		URL = url

		# Start the Selenium web browser
		chrome_options = Options()
		#chrome_options.add_argument("--headless")

		# Load up the initial URL 
		# scroll all the way down to load all doctors
		browser = Chrome(options=chrome_options)
		browser.get(URL)
		time.sleep(3)
		sim_scroll(browser, browser.find_elements_by_css_selector('div.section-layout.section-scrollbox')[1], max_results)

		# Parse the initial URLs provided in the url array
		main_html = browser.page_source
		main_soup = BeautifulSoup(main_html, 'html.parser')

		# Find all places in our google maps result search
		google_results = main_soup.find_all("a", {"class": "a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd"})
	
		for google_result in google_results:
			doctor_name = google_result['aria-label']
			doctor_link = google_result['href']

			# Load the doctor's page
			browser.get(doctor_link)
			time.sleep(3)
			doc_html = browser.page_source
			doc_soup = BeautifulSoup(doc_html, 'html.parser')
			doc_results = doc_soup.find_all("div", {"class": "h0ySl-wcwwM"})[0]

			#If no review, continue
			if doc_results.find("span", class_="OAO0-ZEhYpd-vJ7A6b").find("button", class_="widget-pane-link") is None:
				continue

			# Click on the "Reviews" link button for that doctor
			doc_reviews_button_label = doc_results.find("span", class_="OAO0-ZEhYpd-vJ7A6b").find("button", class_="widget-pane-link")['aria-label']
			#print(doc_reviews_button_label)
			doc_reviews_button_elem = browser.find_element_by_xpath('//button[text()="{0}"]'.format(doc_reviews_button_label))
			ActionChains(browser).click(doc_reviews_button_elem).perform()

			# Parse the reviews string. Remove commas for > 1000
			doc_num_reviews = parse('{:d} reviews', doc_reviews_button_label.replace(',', ''))
			#If one review, continue
			if doc_num_reviews is None:
				continue
			print(doc_num_reviews[0])

			# Scroll down to load all reviews
			time.sleep(3)
			sim_scroll(browser, browser.find_element_by_css_selector('div.section-layout.section-scrollbox'), doc_num_reviews[0])
			doc_reviews_html = browser.page_source
			doc_reviews_soup = BeautifulSoup(doc_reviews_html, 'html.parser')
			#print(doc_reviews_soup)

			# Click all of the "More..." buttons
			expand_more_buttons = browser.find_elements_by_xpath('//button[text()="{0}"]'.format('More'))
			for button in expand_more_buttons:
				ActionChains(browser).click(button).perform()

			# Get source after we Clicked all of the More buttons
			time.sleep(0.5)
			doc_reviews_html = browser.page_source
			doc_reviews_soup = BeautifulSoup(doc_reviews_html, 'html.parser')

			# Do the review fetching into a CSV file
			reviews_results = doc_reviews_soup.find_all("div", {"class": "ODSEW-ShBeI-content"})

			for review_result in reviews_results:
				#print(review_result.prettify())
				review_stars = review_result.find("span", class_="ODSEW-ShBeI-H1e3jb")['aria-label']
				review_text = review_result.find("span", class_="ODSEW-ShBeI-text").text.strip()
				csvwriter.writerow([location, doctor_name, review_stars, review_text])
				#print(review_stars)
				#print(review_text)



		print(len(google_results))

	print("\n === Next URL === \n")
			

