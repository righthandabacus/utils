# -*- coding: utf-8 -*-

"""A browser class as a wrapper for selenium
"""

import os
import signal

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of, title_contains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

__all__ = ['browser']

__FILEDIR = os.path.dirname(os.path.realpath(__file__))

class browser:
    """browser object: Wrapper for selenium"""
    def __init__(self, width=1200, height=800, driver="chrome", headless=True, **kwargs):
        """create and initialize selenium"""
        if driver == "chrome":
            try:
                options = kwargs['chrome_options']
            except KeyError:
                options = webdriver.ChromeOptions()
            options.add_argument('window-size={}x{}'.format(width, height))
            options.add_argument('disable-web-security')  # allow cross-site XHR to download images
            # use user prefs:
            # options.add_argument('user-data-dir=Users/<username>/Library/Application Support/Google/Chrome/Default')
            # mac dir: Users/<username>/Library/Application Support/Google/Chrome/Default
            if headless:
                options.add_argument('headless') # run headless Chrome
            self._driver = webdriver.Chrome(options=options)
        elif driver == "phantomjs":
            # override user agent string and bug workaround by default to turn off Selenium ghostdriver log
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap.update({
                "phantomjs.page.settings.userAgent":
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"
               ,"phantomjs.page.settings.loadImages": True
            })
            self._driver = webdriver.PhantomJS(desired_capabilities=dcap, service_log_path=os.path.devnull)
            self._driver.set_window_size(width, height)
        elif driver == "firefox":
            # TODO enrich this
            self._driver = webdriver.Firefox()
        else:
            raise NotImplementedError("Unrecognized driver %s" % driver)

    def __del__(self):
        """close selenium browser at object destruct"""
        self.quit()

    def __enter__(self):
        "for context manager"
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        "Just close. Exceptions are ignored"
        print("Closing browser")
        self.quit()

    def quit(self):
        """close this browser and render it not functional"""
        if self._driver:
            self._driver.service.process.send_signal(signal.SIGTERM) # kill child proc
            #self._driver.close()
            self._driver.quit()
            self._driver = None

    def user_agent(self):
        """return the browser user-agent string"""
        return self._driver.execute_script("return navigator.userAgent")

    def cookies(self):
        """return all cookies as a python dict"""
        biscus = self._driver.manage().cookies()
        if not biscus:
            # IE and FF, cannot read cookies like above
            cookiestring = self._driver.execute_script("return document.cookie")
            biscus = {}
            for cookie in cookiestring.split("; "):
                key, val = cookie.split("=", 1)
                biscus[key] = val
        return biscus

    def __getattr__(self, name):
        """pass through all unrecognized webdriver functions and attributes"""
        return getattr(self._driver, name)

    def wait_until_staled(self, element, timeout=30):
        WebDriverWait(self._driver, timeout).until(staleness_of(element))

    def is_ready(self):
        """Return True iff the page is loaded"""
        return self._driver.execute_script("return document.readyState === 'complete'")

    def get_everything(self):
        """Extract everything from the DOM
        Returns:
            A list of lists, each of them has the following elements:
            ['element','xpath','visible','x','y','w','h','fg','bg','font','attrs','text','html']
            which element is the DOM object and other are string or numbers
        """
        scriptpath = os.path.join(__FILEDIR, 'get_everything.js')
        js = open(scriptpath).read()
        ret = self._driver.execute_script(js)
        return ret

    def get_xpath(self, element):
        scriptpath = os.path.join(__FILEDIR, 'get_xpath.js')
        js = open(scriptpath).read()
        ret = self._driver.execute_script(js, element)
        return ret

    def get_all_attrs(self, element):
        js = '''
            var items = {};
            for (index = 0; index < arguments[0].attributes.length; ++index) {
                items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
            };
            return items;
        '''
        ret = self._driver.execute_script(js, element)
        return ret

    def save_page_source(self, filename):
        open(filename, 'wb').write(self._driver.page_source.encode('utf8'))

    def save_rendered_html(self, filename):
        html = self._driver.execute_script('return document.documentElement.outerHTML;')
        open(filename, 'wb').write(html.encode('utf8'))

    def is_page_ready(self):
        state = self._driver.execute_script('return document.readyState')
        return state == 'complete'

    def capture_image(self, url):
        """re-fetch the URL image and convert it into base64 encoded binary,
        then save into a span element under document

        Capture by XHR, code derived from
        https://crosp.net/blog/software-development/web/download-images-using-webdriverio-selenium-webdriver/

        See also https://stackoverflow.com/questions/934012/get-image-data-in-javascript for promise syntax
        """
        scriptpath = os.path.join(__FILEDIR, 'download_img.js')
        js = open(scriptpath).read()
        self._driver.execute_script(js, url)
        element = self._driver.find_element_by_id("base64imagedownload")  # expect implicit wait
        if element:
            return self._driver.execute_script("return document.getElementById('base64download').textContent")
        return None  # failed to download the image

def _example():
    "Example of using webdriver"
    # Create a new instance of the Firefox driver
    with browser(driver="firefox") as driver:
        # go to the google home page
        driver.get("http://www.google.com")
        # the page is ajaxy so the title is originally this:
        print(driver.title)
        # find the element that's name attribute is q (the google search box)
        inputElement = driver.find_element_by_name("q")
        # type in the search
        inputElement.send_keys("cheese!")
        # submit the form (although google automatically searches now without submitting)
        inputElement.submit()
        # we have to wait for the page to refresh, the last thing that seems to be updated is the title
        WebDriverWait(driver, 10).until(title_contains("cheese!"))
        # You should see "cheese! - Google Search"
        print(driver.title)

# vim:set fdm=indent ts=4 sw=4 sts=4 bs=2 et:
