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
    # User input about a desired flight
    origin = "SLC"
    destination = "LAX"
    startdate = "2023-01-06"
    #enddate = "2023-01-09"

    # Assembling the url
    url = "https://www.kayak.com/flights/" + origin + "-" + destination + "/" + startdate # + "/" + enddate
    
    # Loading the selenium driver.
    # It will open a chorme page, that will accomplish the scraping
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome("chromedriver.exe")
    driver.implicitly_wait(20)
    driver.get(url)
    
    # From what I udnerstand, it allows the page to load before we proceed
    # I might be wrong though
    sleep(2)


    # Here, we just load more and more results on a page.
    # Technically, we can do it any number of times
    for i in range(5):
        try:
            more_btn = driver.find_element(By.XPATH, "//a[contains(text(), 'Show more results')]")
            more_btn.click()
            sleep(2)
        except:
            continue

    # Now, "souping" the data
    soup=BeautifulSoup(driver.page_source, 'lxml')

    deptimes = soup.find_all('span', attrs={'class': 'depart-time base-time'})

    # These are ALL of the meridiems. Have to split them for
    # the ones corresponding to departures and ones to arrivals
    meridiem = soup.find_all('span', attrs={'class': 'time-meridiem meridiem'})
    mer_dept = meridiem[::2]
    mer_arr = meridiem[1::2]



    arrtimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
    stops = soup.find_all('span', attrs={'class': 'stops-text'})
    prices = soup.find_all('span', attrs={'class': 'price-text'})


    data = {} 
    counter = 0
    for dep, arriv, stps, price, mr_1, mr_2 in zip(deptimes, arrtimes, stops, prices, mer_dept, mer_arr):
        array = []
        array.append(dep.string + ' ' + mr_1.string)
        array.append(arriv.string + ' ' + mr_2.string)
        array.append(stps.string[1:])
        array.append(price.string[1:])
        data[counter] = array 
        counter += 1
    
    # data = {}

    # for link in soup.find_all('a'):
    #     link_address = link.get('href')
    #     link_text = link.string
    #     data[link_text] = link_address

    # data = soup.get_text()
    # data = soup
    return render(request, 'pullFlights/result.html', {'data':data})