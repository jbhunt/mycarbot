# imports
import re
import time
import numpy as np
from selenium import webdriver as swd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from .utilities import (
    wait_for_element,
    click_button,
    HeadlessChromeDriver,
    ScrapingError
)

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

def _update_distance(driver, target_distance):
    """
    this function sets the search distance to the option closest to the target
    distance
    """

    import pdb; pdb.set_trace()

    #
    search_result, distance_drawer = wait_for_element(
        driver,
        '//div[@id="Distance"]'
    )
    if not search_result:
        return False

    click_result = click_button(distance_drawer)
    if not click_result:
        return False

    # wait for the drawer to expand
    search_result, distance_drawer_opened = wait_for_element(
        driver,
        '//div[@class="drawer expanded"][@id="Distance"]'
    )
    if not search_result:
        return False

    # get the valid distance options
    distance_options = np.array([
        int(el.text.rstrip(' miles'))
            for el in distance_drawer_opened.find_elements_by_xpath('//option[contains(text(), "miles")]')
    ])

    # wait for the dropdown menu to become visible
    search_result, distance_dropdown = wait_for_element(
        distance_drawer_opened,
        '//div[starts-with(@class, "kmx-menu")]',
        condition='visible'
        )
    if not search_result:
        return False

    # expand the distance dropdown menu
    click_result = click_button(distance_dropdown)
    if not click_result:
        return False

    # wait for list to expand
    search_result, distance_dropdown_expanded = wait_for_element(
        distance_drawer_opened,
        '//div[@class="kmx-menu kmx-menu--open"]',
        condition='present'
    )
    if not search_result:
        return False

    # instantiate the list of clickable distance options
    distance_list = distance_dropdown_expanded.find_elements_by_tag_name('li')

    # if no target distance selected go ahead and click the Nationwide option
    if target_distance in [None, 'nationwide', 'Nationwide']:
        for entry in distance_list:
            if entry.text == 'Nationwide':
                try:
                    distance_button = WebDriverWait(distance_dropdown, 15).until(
                        EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(), "{entry.text}")]'))
                    )
                except TimeoutException:
                    return False
                click_result = click_button(distance_button)
                if not click_result:
                    return False

    # select the valid distance closest to the target distance
    else:
        closest = distance_options[np.argmin(abs(distance_options - target_distance)).item()]
        for entry in distance_list:
            if 'miles' in entry.text:
                distance = int(entry.text.rstrip(' miles'))
                if distance == closest:
                    print(f'Setting distance to {distance} miles')
                    try:
                        distance_button = WebDriverWait(distance_dropdown, 15).until(
                            EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(), "{entry.text}")]'))
                        )
                    except TimeoutException:
                        return False
                    click_result = click_button(distance_button)
                    if not click_result:
                        return False

    # wait for the new results to load
    search_result, results_section = wait_for_element(
        driver,
        '//section[@id="search-results"][@style="overflow: hidden;"]',
        condition='present',
        attempt=15,
        timeout=1
    )
    if not search_result:
        return False

    # the style attribute will change to an empty string when the new results are loaded
    while results_section.get_attribute('style') != '':
        continue

    return True

def scrape(
    make='subaru',
    model='forester',
    zipcode=80247,
    distance=None,
    year=None,
    price=None,
    mileage=None,
    headless=False
    ):
    """
    """

    if headless:
        raise ScrapingError('Headless mode is not supported for CarMax')
        # driver = HeadlessChromeDriver()
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
    update_result = _update_distance(driver, distance)
    if not update_result:
        raise ScrapingError('Failed to set distance')

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
