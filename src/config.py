from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait


# This class is created to configure the web driver
class WebDriverSetup:
    def __init__(self, implicit_wait_time=10, headless=False):
        self.implicit_wait_time = implicit_wait_time
        self.headless = headless
        self.user_agent = self.get_random_desktop_user_agent()
        self.driver = self._get_webdriver()
        self.wait = self._get_wait_object(self.driver, implicit_wait_time)

    @staticmethod
    def get_random_desktop_user_agent():
        ua = UserAgent()
        while True:
            user_agent = ua.random
            if "Mobile" not in user_agent and "Android" not in user_agent and "iPhone" not in user_agent:
                return user_agent

    def _get_webdriver(self):
        # We configure the driver
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f"user-agent={self.user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(self.implicit_wait_time)
        return driver

    def _get_wait_object(self, driver, time):
        # We configure a WebDriverWait object
        if self.headless is True:
            wait = WebDriverWait(driver, time*2)
        else:
            wait = WebDriverWait(driver, time)
        return wait

    def get_driver(self):
        return self.driver

    def get_wait(self):
        return self.wait

    def quit(self):
        self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.quit()


# This class is created to check the correctness of the search filter
# I deliberately named it in violation of the rules to reflect its function.
class element_value_matches:
    def __init__(self, locator, expected_values):
        self.locator = locator
        self.expected_values = expected_values

    def __call__(self, driver):
        elements = driver.find_elements(*self.locator)
        if len(elements) >= 4:  # Ensure we have at least 4 elements
            filter_min_element = elements[2]
            filter_max_element = elements[3]

            filter_min_text = filter_min_element.get_attribute("value")
            filter_max_text = filter_max_element.get_attribute("value")

            return filter_min_text == self.expected_values[0] and filter_max_text == self.expected_values[1]
        return False
