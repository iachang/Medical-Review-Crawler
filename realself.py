import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time 

urls = ['https://www.realself.com/drsearch?keyword=plastic%20surgery&location=Los%20Angeles,%20CA,%20USA&lat=34.0522342&lng=-118.2436849&city=Los%20Angeles&state=CA&country=US&virtualConsultation=true&range=60&page=']
max_results = 30


# Prevent reCaptcha by adding Header info
header = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0" ,
    'Referer':'https://www.google.com/'
}

for url in urls:
	for page_num in range(10, max_results + 10, 10):

		URL = url + str(page_num // 10)
		print(URL)

		main_page = requests.get(URL,headers=header)
		main_soup = BeautifulSoup(main_page.content, 'html.parser')
		time.sleep(2)
		print(main_soup)

		doctor_results = main_soup.find_all("div", {"class": "Media-body"})

		#print(doctor_results)
		for doctor_result in doctor_results:
			doctor_name = doctor_result.find('a', class_='Headline--6')
			doctor_main_review = doctor_result.find('a', class_='Link--primary')
			print(doctor_result)
			print(doctor_name.text.strip())
			print(doctor_main_review['href'])




	print("\n === Next URL === \n")
			