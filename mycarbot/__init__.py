from selenium import webdriver as swd
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

class ScrapingError(Exception):
    def __init__(self, message):
        super().__init__(message)
        return

class HeadlessChromeDriver(swd.Chrome):
    """
    a subclass of the Chrome driver object which runs headless
    """

    def __init__(self, *args, **kwargs):
        """
        """

        # set headless state
        options = Options()
        options.headless = True

        # create fake user agent (this is necessary for the headless driver to work)
        ua = UserAgent()
        options.add_argument(f'user-agent={ua.chrome}')

        # store these internally for the restart method
        self._args = args
        self._kwargs = kwargs

        # init
        kwargs['chrome_options'] = options
        super().__init__(*args, **kwargs)

        return

    def reload(self):
        """
        close and reopen the driver
        """

        # close
        self.close()

        # reload
        super().__init__(*self._args, **self._kwargs)

        return
