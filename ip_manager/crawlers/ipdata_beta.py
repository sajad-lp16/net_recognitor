from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

# url = 'https://www.facebook.com/'
url = 'http://tohidi:174pasS@www.youtube.com/'
# url = 'https://www.google.com/'

# proxy_ = "172.16.0.54:808"
# proxy_ = "172.16.0.54:808"

proxy_ = '172.16.0.55'

proxy = Proxy()

proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = proxy_
proxy.ssl_proxy = proxy_

# proxy.socks_username = 'tohidi'
# proxy.socks_password = '174pasS'

cap = webdriver.DesiredCapabilities.FIREFOX
proxy.add_to_capabilities(cap)

web = webdriver.Firefox(desired_capabilities=cap)
with web as driver:
    wait = WebDriverWait(driver, timeout=20)
    driver.get(url)

    # alert = driver.switch_to.alert
    # alert.send_keys('tohidi\ue004174pasS')

    sleep(100)
