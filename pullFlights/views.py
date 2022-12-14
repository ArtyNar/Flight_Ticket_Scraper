# Django imports
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect

# Selenium imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from time import sleep

# Our scraper!
def scrape(request):
    if request.method == 'POST':
        origin = request.POST.get('departure', '')
        destination = request.POST.get('destination', '')
        startdate = request.POST.get('startdate', '')

        #enddate = "2023-01-09"

        # # Assembling the url
        url = "https://www.kayak.com/flights/" + origin + "-" + destination + "/" + startdate # + "/" + enddate
        
        # Loading the selenium driver.
        # It will open a chorme page, that will accomplish the scraping
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome("chromedriver.exe")
        driver.implicitly_wait(20)
        driver.get(url)
        
        # From what I udnerstand, it allows the page to load before we proceed
        # I might be wrong though
        # sleep(2)

        # Here, we just load more and more results on a page.
        # Technically, we can do it any number of times
        for _ in range(1):
            try:
                more_btn = driver.find_element(By.XPATH, "//a[contains(text(), 'Show more results')]")
                more_btn.click()
                sleep(2)
            except:
                continue

        # Now, "souping" the data
        soup=BeautifulSoup(driver.page_source, 'lxml')

        # Gets the time of a departure
        deptimes = soup.find_all('span', attrs={'class': 'depart-time base-time'})

        # These are ALL of the meridiems. Have to split them for
        # the ones corresponding to departures and ones to arrivals
        meridiem = soup.find_all('span', attrs={'class': 'time-meridiem meridiem'})
        mer_dept = meridiem[::2]
        mer_arr = meridiem[1::2]

        # Gets the time of the arrival, number of stops, company, and the price
        arrtimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
        stops = soup.find_all('span', attrs={'class': 'stops-text'})
        prices = soup.find_all('span', attrs={'class': 'price-text'})
        company = soup.find_all('div', attrs={'class': 'bottom'})

        # Our data will be contained here 
        data = []

        # Used for ids
        counter = 1
        for dep, arriv, stps, price, mr_1, mr_2, comp in zip(deptimes, arrtimes, stops, prices, mer_dept, mer_arr, company[::3]):
            # Creating a dictionary for each entry
            inner_dict = {}

            # Grabbing the data, distributing it into a dictionary
            inner_dict['id'] = counter
            inner_dict['departure'] = dep.string + ' ' + mr_1.string
            inner_dict['arrival'] = arriv.string + ' ' + mr_2.string
            inner_dict['stops'] = stps.string.strip()
            inner_dict['price'] = price.string.strip()
            inner_dict['company'] = comp.string.strip()

            # Appending everything to a data array
            data.append(inner_dict) 
            
            # Used for assigning id's to data points
            counter += 1

        return render(request, 'pullFlights/result.html', {'data':data})
    else:
        return render(request, 'pullFlights/result.html', {})
