# imports
import re
import numpy as np
from selenium import webdriver as swd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# constants
CHROMEDRIVERPATH = '/usr/bin/chromedriver'

class CarmaxVehicle(object):
    """
    """

    def __init__(self, tag):
        """
        """

        super().__init__()

        #
        self._stockno = int(re.findall('StockNumber: \d*', tag.get_attribute('data-clickprops'))[0].strip('StockNumber: '))

        #
        self._year, self._make = tag.find_element_by_class_name('year-make').text.split()
        self._model = tag.find_element_by_class_name('model-trim').text.split()[0]
        self._price = int(tag.find_element_by_class_name('price').text.strip('*').strip('$').replace(',',''))
        self._mileage = int(re.findall('\d*K', tag.find_element_by_class_name('miles').text)[0].strip('K')) * 1000

        return

    @property
    def stockno(self):
        return self._stockno

    @property
    def link(self):
        return f'https://www.carmax.com/car/{self.stockno}'

    @property
    def year(self):
        return int(self._year)

    @property
    def make(self):
        return self._make

    @property
    def model(self):
        return self._model

    @property
    def trim(self):
        return self._trim

    @property
    def price(self):
        return self._price

    @property
    def mileage(self):
        return self._mileage

def scrape(make='subaru', model='forester', zipcode=80247, distance='nationwide', year=(2016,2018), price=None, mileage=None):
    """
    """

    #
    url = f'https://www.carmax.com/cars/{make}/{model}'

    #
    driver = swd.Chrome(CHROMEDRIVERPATH)
    driver.get(url)

    # set the zipcode
    box = driver.find_element_by_id('zip')
    box.clear()
    box.send_keys(zipcode)
    box.send_keys(swd.common.keys.Keys.RETURN)

    # set the distance

    # gather clickable options
    items = driver.find_elements_by_class_name('kmx-menu-item')

    # a specific distance in miles
    if type(distance) == int:
        valid = np.array([25, 50, 75, 100, 250, 500])
        closest = valid[np.argmin(abs(valid - distance)).item()]
        for item in items:
            if item.text == f'{closest} Miles':
                item.click()
                break

    # nearest CarMax
    elif distance == 'nearest-store':
        for item in items:
            if item.text == 'Nearest store':
                item.click()

    # nationwide search
    else:
        for item in items:
            if item.text == 'Nationwide':
                item.click()

    # load all results (this can be done better for sure)
    try:
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'See More Matches')]"))
        )
        element.click()
    except:
        pass

    # find all entries
    tiles = [tile for tile in driver.find_elements_by_class_name('car-tile') if tile.text != '']

    #
    cars = list()

    #
    for tag in tiles:

        # init vehicle object
        car = CarmaxVehicle(tag)

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

    return cars
