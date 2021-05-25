# mycarbot
This package scrapes data from the website of used car sellers using the Python bindings for Selenium. Supported sellers include Carvana, CarMax, and www.cars.com.

# Basic usage
```Python
from mycarbot import carvana
cars = carvana.scrape(make='subaru', model='forester', year=(2016, 2018))
for car in cars:
    print(f'{car.year}, {car.price}, {car.mileage}')
2018, 22000, 60000
... 
```
