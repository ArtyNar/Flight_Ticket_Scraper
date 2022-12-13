# Django imports
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions

def scrape(request):
    site = 'https://www.kayak.com/flights/SLC-LAX/2023-01-12/2023-01-19s'

    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome("chromedriver.exe")
    driver.implicitly_wait(20)
    driver.get(site)

    captcha = driver.find_element(By.XPATH, "//iframe[@role='presentation']")
    captcha.click()

    soup = BeautifulSoup(driver.page_source, 'lxml')
    data = soup.title

    # # Creates a session
    # session = requests.Session()
    # session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    
    # page = session.get(site)
    # soup = BeautifulSoup(page.text, 'html.parser')
    
    # data = {}

    # for link in soup.find_all('a'):
    #     link_address = link.get('href')
    #     link_text = link.string
    #     data[link_text] = link_address

    # data = soup.get_text()
    # data = soup
    return render(request, 'pullFlights/result.html', {'data':data})