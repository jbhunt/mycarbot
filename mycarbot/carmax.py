# imports
import re
import time
import numpy as np
from selenium import webdriver as swd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from . import HeadlessChromeDriver, wait_for_element, ScrapingError
from selenium.common.exceptions import TimeoutException

# constants

#
CHROMEDRIVERPATH = '/usr/bin/chromedriver'

# these are the valid distance options
VALID_DISTANCE_OPTIONS = [
    25, 50, 75, 100, 250, 500, 'Nationwide'
]

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

def _set_store(driver, zipcode):
    """
    """

    return

def _set_distance(driver, target_distance):
    """
    """

    #
    distance_drawer = driver.find_element_by_xpath('//div[@class="drawer"][@id="Distance"]')
    distance_drawer.click()

    # wait for the drawer to expand
    try:
        distance_drawer_opened = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="drawer expanded"][@id="Distance"]'))
        )
    except TimeoutException:
        raise ScrapingError('Unable to locate the distance drawer element')

    # wait for the dropdown menu to become visible
    try:
        distance_dropdown = WebDriverWait(distance_drawer_opened, 15).until(
            EC.visibility_of_element_located((By.XPATH, '//div[starts-with(@class, "kmx-menu")]'))
        )
    except TimeoutException:
        raise ScrapingError('Unable to locate the distance dropdown menu element')

    # expand the distance dropdown menu
    distance_dropdown.click()

    # wait for list to expand
    try:
        distance_dropdown = WebDriverWait(distance_drawer_opened, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="kmx-menu kmx-menu--open"]'))
        )
    except TimeoutException:
        raise ScrapingError('Unable to locate the expanded distance dropdown menu element')

    # grab the list element
    while True:
        distance_list = [el for el in distance_dropdown.find_elements_by_tag_name('li') if 'miles' in el.text]
        if len(distance_list) != 6:
            continue
        valid_distances = list()
        for entry in distance_list:
            result = re.findall('\d+', entry.text)
            if len(result) != 0:
                valid_distances.append(int(result[0]))
        if len(valid_distances) == len(distance_list):
            break

    # reinstantiate the list of distance options
    distance_list = distance_dropdown.find_elements_by_tag_name('li')

    # if no target distance selected go ahead and click the Nationwide option
    if target_distance in [None, 'nationwide', 'Nationwide']:
        for entry in distance_list:
            if entry.text == 'Nationwide':
                distance_button = WebDriverWait(distance_dropdown, 15).until(
                    EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(), "{entry.text}")]'))
                )
                for itry in range(5):
                    try:
                        distance_button.click()
                    except:
                        time.sleep(0.1)

    # select the valid distance closest to the target distance
    else:
        valid_distances = np.array(valid_distances)
        closest = valid_distances[np.argmin(abs(valid_distances - target_distance)).item()]
        for entry in distance_list:
            if 'miles' in entry.text:
                distance = int(entry.text.rstrip(' miles'))
                if distance == closest:
                    print(f'Setting distance to {distance} miles')
                    distance_button = WebDriverWait(distance_dropdown, 15).until(
                        EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(), "{entry.text}")]'))
                    )
                    for itry in range(5):
                        try:
                            distance_button.click()
                        except:
                            time.sleep(0.1)

    search_results = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//section[@id="search-results"][@style="overflow: hidden;"]'))
    )
    while search_results.get_attribute('style') != '':
        continue

    return

def scrape(make='subaru', model='forester', zipcode=80247, distance=None, year=(2016,2018), price=None, mileage=None, headless=True):
    """
    """

    if headless:
        driver = HeadlessChromeDriver()
    else:
        driver = swd.Chrome('/usr/bin/chromedriver')

    # set the location
    url = f'https://www.carmax.com/stores/search?keyword={zipcode}'
    driver.get(url)
    buttons = driver.find_elements_by_xpath('//button[starts-with(@id, "setUserStore")]')
    buttons[0].click() # the closest store should be the first button

    # wait for the redirect page to load
    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: driver.current_url != url)

    #
    url = f'https://www.carmax.com/cars/{make}/{model}'
    driver.get(url)

    # set the distance
    _set_distance(driver, distance)

    # load all results
    while True:
        try:
            see_more_results_button = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//a[starts-with(@class, "kmx-button")][contains(text(), "See More Matches")]'))
            )
            for itry in range(5):
                try:
                    see_more_results_button.click()
                except:
                    time.sleep(0.1)
        except TimeoutException:
            break

    # determine how many cars matched
    header_value = driver.find_element_by_xpath('//div[@id="results-header-wrapper"]//span[starts-with(@class, "header-value")]')
    ncars = int(header_value.text)

    # find all entries
    tiles = [tile for tile in driver.find_elements_by_xpath('//article[@class="car-tile"]') if tile.text != ''][:ncars]

    print(f'{len(tiles)} cars found!')

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
