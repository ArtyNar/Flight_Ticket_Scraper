# Django imports
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect

# csv
import csv

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
        
        # Here, we just load more and more results on a page.
        # Technically, we can do it any number of times
        for _ in range(5):
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

        # Gets the time of the arrival, number of stops, company, class of a ticket, and the price
        arrtimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
        stops = soup.find_all('span', attrs={'class': 'stops-text'})
        prices = soup.find_all('span', attrs={'class': 'price-text'})
        company = soup.find_all('div', attrs={'class': 'bottom'})
        ticket_class = soup.find_all('span', attrs={'class': 'label'})
        links = soup.find_all('a', attrs={'class': 'booking-link'})

        # Our data will be contained here 
        data = []

        # Used for displaying a histogram
        prices_arr = []

        # Used for ids
        counter = 1
        for dep, arriv, stps, price, mr_1, mr_2, comp, tclass, link in zip(deptimes, arrtimes, stops, prices, mer_dept, mer_arr, company[::3], ticket_class, links):
            # Creating a dictionary for each entry
            inner_dict = {}

            # Grabbing the data, distributing it into a dictionary
            inner_dict['id'] = counter
            inner_dict['departure'] = dep.string + ' ' + mr_1.string
            inner_dict['arrival'] = arriv.string + ' ' + mr_2.string
            inner_dict['stops'] = stps.string.strip()
            inner_dict['price'] = price.string.strip()
            inner_dict['company'] = comp.string.strip()
            inner_dict['class'] = tclass.string.strip()
            inner_dict['link'] = link.get('href')

            # Used for displaying a histogram
            # Puts all the prices in a correct format
            data_point = [f"{counter} {comp.string.strip()}",
                          price.string.strip().strip('$')]
            prices_arr.append(data_point)

            # Appending everything to a data array
            data.append(inner_dict) 
            
            # Used for assigning id's to data points
            counter += 1

        # Used to determine if nothing was returned
        empty = None
        if len(data) == 0:
            empty = 1

        # Calculating statistics
        stats = {}
        numerics = []
        for point in data:
            numerics.append(int(point['price'][1:]))
        try:
            stats['min'] = min(numerics)
            stats['max'] = max(numerics)
            stats['average'] = str(round(sum(numerics)/len(numerics), 2))
        except:
            pass
        return render(request, 'pullFlights/result.html', {'data':data, 'prices':prices_arr, 'empty':empty, 'stats':stats})
    else:
        return render(request, 'pullFlights/result.html', {})

# Allows the user to search for airport codes
def see_codes(request):
    airports = []
    with open('data/airport-codes.csv', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                dict = {}
                dict['id'] = line_count
                dict['name'] = row[0]
                dict['country'] = row[1]
                dict['code'] = row[2]
                airports.append(dict) 
                line_count += 1
    return render(request, 'pullFlights/codes.html', {'airports':airports , 'range':range(len(airports))})

