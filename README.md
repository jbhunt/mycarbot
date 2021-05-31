# mycarbot
This package scrapes data from used car sellers using the Python bindings for Selenium. Supported sellers include Carvana, CarMax, and www.cars.com.

# Current status
| Seller       | Status  |
| ------------ | ------- |
| Carvana      | Working |
| Carmax       | Working |
| www.cars.com | Broken  |
Update on May 31, 2021.

# Basic usage
For each used car seller, there is a corresponding module. Each of these modules has a `scrape` function that is used to collect data from each seller. The first two keyword arguments specify the make and model of the target vehicle.
```Python
from mycarbot import carvana
cars = carvana.scrape(make='subaru', model='forester')
for car in cars:
    print(f'{car.year}, {car.price}, {car.mileage}')
2020, 28990, 7457
... 
```

The `scrape` function also accepts several keyword arguments that filters the scraped data. For example, you can specify the minimum and maximum mileage.
```Python
cars = carvana.scrape(make='subaru', model='forester', mileage=(0, 100000))
``` 

If you want to run the webdriver headless (i.e., no window), you can set the `headless` flag.
```Python
cars = scrape(make='subaru', model='forester', headless=True)
```

# Dependencies
1. Chrome
2. ChromeDriver
3. Selenium
4. fake-useragent

I used [this guide](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/) (steps 1 and 2) to install Chrome and ChromeDriver on Ubuntu 18.04. To install Selenium and fake-useragent you can execute `pip install selenium` and `pip install fake-useragent` in the terminal.
