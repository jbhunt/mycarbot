import time
from selenium import webdriver as swd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def wait_for_element(driver, xpath, condition='present', attempt=5, timeout=1):
    """
    attempt to locate an element multiple times with a delay in between each call

    returns
    -------
    result
        result of the function either True or False
    element
        target element if result is True else None
    condition
        the expected condition to wait for (as a string)
    """

    result = False

    #
    if condition == 'present':
        condition_function = EC.presence_of_element_located
    elif condition == 'visible':
        condition_function = EC.visibility_of_element_located
    else:
        return result, None

    for iattempt in range(attempt):
        try:
            element = WebDriverWait(driver, timeout).until(
                condition_function((By.XPATH, xpath))
            )
            result = True
            break
        except TimeoutException:
            continue

    if result:
        return result, element
    else:
        return result, None

def click_button(button, attempt=5, timeout=1):
    """
    attempt to click a clickable element
    """

    result = False

    for iattempt in range(attempt):
        try:
            button.click()
            result = True
            break
        except WebDriverException:
            time.sleep(timeout)

    return result

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

    def close_and_reopen(self):
        """
        close and reopen the driver
        """

        # close
        self.close()

        # reload
        super().__init__(*self._args, **self._kwargs)

        return
