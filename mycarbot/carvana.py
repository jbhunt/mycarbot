# absolute imports
import re
import numpy as np
from selenium import webdriver as swd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

# relative imports
from .utilities import (
    wait_for_element,
    click_button,
    HeadlessChromeDriver,
    ScrapingError
)

class CarvanaVehicle():
    """
    """

    def __init__(self, tag):
        """
        """

        info = tag.find_element_by_xpath('//div[@data-test="MakeModel"]')
        make_and_year, model = info.text.split('\n')
        year, make = make_and_year.split()
        self._year = int(year)
        self._make = make
        self._model = model
        self._price = int(
            tag.find_element_by_xpath('//div[@data-test="Price"]').text.strip('$').replace(',', '')
        )
        self._trim = tag.find_element_by_xpath('//div[@data-test="TrimMileage"]/div[@class="trim"]').text
        self._mileage = int(
            tag.find_element_by_xpath('//div[@data-test="TrimMileage"]/div[@class="mileage"]').text.rstrip(' miles').replace(',', '')
        )

        return

    @property
    def link(self):
        return self._link

    @property
    def trim(self):
        return self._trim

    @property
    def make(self):
        return self._make

    @property
    def model(self):
        return self._model

    @property
    def year(self):
        return int(self._year)

    @property
    def price(self):
        return self._price

    @property
    def mileage(self):
        return self._mileage

def scrape(make='subaru', model='forester', year=None, price=None, mileage=None, zipcode=67005, headless=False):
    """
    search for a specific car by make, model, year, price, and mileage

    keyword
    -------
    make : str
        vehicle make
    model : str
        vehicle model
    year : None, int, tuple
        the exact year of the vehicle or a range of years
    price : None or tuple
        the price range
    mileage : None or tuple
        the range of mileage
    headless:
        flag which specifies whether to run the driver as headless (no window)

    returns
    -------
    cars : list
        list of vehicle objects
    """

    #
    if headless:
        driver = HeadlessChromeDriver()
    else:
        driver = swd.Chrome('/usr/bin/chromedriver')

    # start on page 1
    ipage = 1

    # initialize and empty list of cars
    cars = list()

    # set the location
    driver.get('https://www.carvana.com/cars')
    location_button = driver.find_element_by_xpath(
        '//button[@data-cv-test="geolocation-button"]'
    )
    location_button.click()
    result, box = wait_for_element(driver, '//input[@name="ZIP CODE"]')
    if not result:
        raise ScrapingError('Could not find the zipcode text box')
    box.send_keys(zipcode)
    result, search_button = wait_for_element(driver, '//button[@data-cv-test="Cv.Search.Geolocation.UpdateButton"]')
    if not result:
        raise ScrapingError('Could not find the search button')
    search_button.click()

    # NOTE - For some reason, the location only updates the second time
    #        the first page is loaded so I am loading it once here.
    url = f'https://www.carvana.com/cars/{make}-{model}?page={ipage}'
    driver.get(url)

    # keep looping through pages until all entries are exhausted
    while True:

        # download the html
        url = f'https://www.carvana.com/cars/{make}-{model}?page={ipage}'
        driver.get(url)

        # check that the location is correct
        location = driver.find_element_by_xpath(
            '//button[@data-cv-test="geolocation-button"]'
        ).text

        # collect all tiles
        tiles = driver.find_elements_by_xpath('//article[@class="result-tile"]')
        if len(tiles) == 0:
            break

        # extract the each entry
        for tag in tiles:

            # init the vehicle object
            car = CarvanaVehicle(tag)

            # filtering

            # by year
            if year != None:
                if type(year) in [list, tuple]:
                    if year[0] <= car.year <= year[1]:
                        cars.append(car)
                else:
                    if car.year == year:
                        cars.append(car)

            # by price
            if price != None:
                if price[0] <= car.price <= price[1]:
                    cars.append(car)

            # by mileage
            if mileage != None:
                if mileage[0] <= car.mileage <= mileage[1]:
                    cars.append(car)

            # no filters
            if year is None and price is None and mileage is None:
                cars.append(car)

        # increment the page number
        ipage += 1

    driver.close()

    return cars
