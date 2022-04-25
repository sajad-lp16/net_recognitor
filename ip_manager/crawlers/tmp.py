from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

ip = "172.16.0.55:808"

chrome_options = Options()
chrome_options.add_argument("--proxy-server=http://" + ip)
web = webdriver.Chrome(options=chrome_options)

url = "https://www.youtube.com"
url2 = "https://www.google.com"
url3 = "https://www.google.com/search?channel=fs&client=ubuntu&q=my+ip"


with web as driver:
    driver.get(url3)
    sleep(50)
