import bs4
import requests

class CarvanaVehicle(object):
    """
    """

    def __init__(self, tag):
        """
        """

        super().__init__()

        # internal property values
        self._link = f"https://www.carvana.com{tag.a.attrs['href']}"
        self._year, self._make = tag.find(attrs={'data-qa':'result-tile-make'}).text.split(' ')
        self._model = tag.find(attrs={'data-qa':'result-tile-model'}).text
        self._price = int(tag.find(attrs={'data-qa':'vehicle-price'}).text.strip(' miles').replace(',',''))
        self._mileage = int(tag.find(attrs={'data-qa':'vehicle-mileage'}).text.strip(' miles').replace(',',''))

        return

    @property
    def link(self):
        return self._link

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

def scrape(make='subaru', model='forester', year=None, price=None, mileage=None):
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

    returns
    -------
    cars : list
        list of vehicle objects
    """

    #test

    # check the type


    # start on page 1
    ipage = 1

    # list of cars
    cars = list()

    # keep looping through pages until all entries are exhausted
    while True:

        # download the html
        url = f'https://www.carvana.com/cars/{make}-{model}?page={ipage}'
        try:
            req = requests.get(url)
        except requests.ConnectionError as e:
            return
        soup = bs4.BeautifulSoup(req.content, 'html.parser')

        # break out if the page is empty
        res = soup.find('div', attrs={'data-qa':'title'})
        if res is not None and res.text == 'We didn’t find any exact matches':
            break

        #
        print(f'scrapping page {ipage} ...')

        # collect all tiles
        tiles = soup.find_all(attrs={'data-qa':'result-tile'})

        # extract the each entry
        for tag in tiles:

            # these are ads
            if tag.a.attrs['data-qa'] == 'styled-link':
                continue

            # these are real vehicle entries
            elif tag.a.attrs['data-qa'] == 'vehicle-link':

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

            # unidentified case
            else:
                continue

        # increment the page number
        ipage += 1

    return cars
