# imports
import re
import numpy as np
from selenium import webdriver as swd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from . import HeadlessChromeDriver

# constants
CHROMEDRIVERPATH = '/usr/bin/chromedriver'

class CarsDotComVehicle():
    """
    """

    def __init__(self, tag):
        """
        """

        title = tag.text.split('\n')[1]
        parts = title.split()
        self._year = int(parts[0])
        self._make = parts[1]
        self._model = parts[2]
        if len(parts) > 3:
            if ' ' in parts:
                self._trim = ' '.join(parts[3])
            else:
                self._trim = parts[-1]
        else:
            self._trim = None

        #
        price = tag.find_element_by_class_name('listing-row__price')
        if price.text != 'Not Priced':
            self._price = int(price.text.strip('$').replace(',',''))
        else:
            self._price = None

        result = re.findall('\n.* mi.\n', tag.text)
        if len(result) == 1:
            mileage = result[0].strip('\n').strip(' mi.').replace(',','')
            if mileage != '--':
                self._mileage = int(mileage)
        else:
            self._mileage = None

    @property
    def year(self):
        return self._year

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
    def mileage(self):
        return self._mileage

    @property
    def price(self):
        return self._price

def scrape(
    make='Subaru',
    model='Forester',
    zipcode=80247,
    year=[2016,2018],
    distance=None,
    mileage=None,
    nresults=20
    ):
    """
    """

    # print('Unfortunately, www.cars.com prevents web scraping.')
    # return

    url = 'https://www.cars.com/'
    driver = HeadlessChromeDriver(CHROMEDRIVERPATH)
    driver.get(url)

    # construct the make and model integer mapping
    makemap = {}
    makeddm = driver.find_element_by_name('makeId')
    modelmap = {}

    # iterate through each model
    for option in makeddm.find_elements_by_tag_name('option'):
        makemap[option.text] = option.get_property('value')
        option.click()

        # iterate through each make
        modelddm = driver.find_element_by_name('modelId')
        for option in modelddm.find_elements_by_tag_name('option'):
            modelmap[option.text] = option.get_property('value')

    # check that the target make and model are valid
    if make not in list(makemap.keys()):
        raise Exception(f'Invalid vehicle make: {make}')

    if model not in list(modelmap.keys()):
        raise Exception(f'Invalid model: {model}')

    # select radius closest to the target distance
    radii = list()
    for option in  driver.find_element_by_name('radius').find_elements_by_tag_name('option'):
        radius = int(option.get_property('value'))
        radii.append(radius)
    if distance is None:
        radius = radii[np.argmin(np.argsort(radii))]
    else:
        radius = radii[np.argmin(np.argsort(abs(np.array(raddi) - distance)))]

    # reload the driver
    driver.reload()

    # url for page 1
    url = (
    f'https://www.cars.com/for-sale/searchresults.action/'
    f'?mdId={modelmap[model]}'
    f'&mkId={makemap[make]}'
    f'&perPage={nresults}'
    f'&rd={radius}'
    f'&searchSource=QUICK_FORM'
    f'&zc={zipcode}'
    )

    #
    driver.get(url)
    tiles = driver.find_elements_by_class_name('listing-row__details')

    # wait for the page to load
    # try:
    #     element = WebDriverWait(driver, 15).until(
    #         EC.presence_of_element_located((By.CLASS_NAME, "page-list"))
    #     )
    #     element.click()
    # except:
    #     import pdb; pdb.set_trace()
    #     return

    # check that the page was downloaded
    # import pdb; pdb.set_trace()

    # determine how many pages there are
    # page_list = driver.find_element_by_class_name('page-list')
    # page_numbers = [int(el.text) for el in page_list.find_elements_by_class_name('not-current')]
    # npages = sorted(page_numbers)[-1]

    #
    vehicles = list()

    # load one page at a time
    # for ipage in range(npages):
    ipage = 1
    while True:

        # reload the driver
        driver.reload()

        # construct the url for the target page number
        url = (
        f'https://www.cars.com/for-sale/searchresults.action/'
        f'?mdId={modelmap[model]}'
        f'&mkId={makemap[make]}'
        f'&page={ipage}'
        f'&perPage={nresults}'
        f'&rd={radius}'
        f'&searchSource=QUICK_FORM'
        f'&zc={zipcode}'
        )

        # download the page
        driver.get(url)

        #
        ipage += 1

        #
        tiles = driver.find_elements_by_class_name('listing-row__details')
        for tile in tiles:
            v = CarsDotComVehicle(tile)
            vehicles.append(v)
        if len(tiles) == 0:
            break

    driver.close()

    return vehicles
