from time import sleep

from celery import shared_task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

from . import data_managers


@shared_task
def crawl_ip_info(ips, many=False):
    url = 'https://ipinfo.io/'
    ip_input_path = '//*[@id="homepage-search-input"]'
    submit_butt_path = '/html/body/div[1]/div[1]/div/div/div/div/div/div[3]/div/div[1]/button'
    data_target = '//*[@id="ipw_main_area"]'
    options = Options()
    options.set_preference('dom.webnotifications.enabled', False)

    web = webdriver.Firefox(options=options)

    with web as driver:
        wait = WebDriverWait(driver, timeout=10)
        driver.get(url)
        wait.until(presence_of_element_located((By.XPATH, ip_input_path)))
        wait.until(presence_of_element_located((By.XPATH, submit_butt_path)))

        ip_box = driver.find_element(By.XPATH, ip_input_path)
        submit_button = driver.find_element(By.XPATH, submit_butt_path)

        if many:
            assert isinstance(ips, list)
            for ip in ips:
                ip_box.send_keys(ip)
                submit_button.click()
                data_source = driver.find_element(By.XPATH, data_target).text
                data_managers.ip_info_manager(data_source)
                sleep(2)
        else:
            ip_box.send_keys(ips)
            submit_button.click()
            sleep(2)
            data_source = driver.find_element(By.XPATH, data_target).text
            return data_managers.ip_info_manager(data_source)


@shared_task
def crawl_ip_registry(ips, many=False):
    url = 'https://ipregistry.co/'
    ip_input_path = '//*[@id="iptocheck"]'
    submit_butt_path = '//*[@id="ipcheck_submit"]'

    options = Options()
    options.set_preference('dom.webnotifications.enabled', False)

    web = webdriver.Firefox(options=options)

    with web as driver:
        wait = WebDriverWait(driver, timeout=10)
        driver.get(url)
        wait.until(presence_of_element_located((By.XPATH, ip_input_path)))
        wait.until(presence_of_element_located((By.XPATH, submit_butt_path)))

        ip_box = driver.find_element(By.XPATH, ip_input_path)
        submit_button = driver.find_element(By.XPATH, submit_butt_path)

        if many:
            assert isinstance(ips, list)
            for ip in ips:
                ip_box.send_keys(ip)
                submit_button.click()
                # call ip_data_store
                sleep(3)
        else:
            ip_box.send_keys(ips)
            submit_button.click()
            return  # ip data store


@shared_task
def crawl_ip_data(ips, many=False):
    url = 'https://ipdata.co/'
    ip_input_path = '//*[@id="searchIP"]'
    submit_butt_path = '//*[@id="searchIPButton"]'

    options = Options()
    options.set_preference('dom.webnotifications.enabled', False)

    web = webdriver.Firefox(options=options)

    with web as driver:
        wait = WebDriverWait(driver, timeout=10)
        driver.get(url)
        wait.until(presence_of_element_located((By.XPATH, ip_input_path)))
        wait.until(presence_of_element_located((By.XPATH, submit_butt_path)))

        ip_box = driver.find_element(By.XPATH, ip_input_path)
        submit_button = driver.find_element(By.XPATH, submit_butt_path)

        if many:
            assert isinstance(ips, list)
            for ip in ips:
                ip_box.send_keys(ip)
                submit_button.click()
                # call ip_data_store
                sleep(3)
        else:
            ip_box.send_keys(ips)
            submit_button.click()
            return  # ip data store


@shared_task
def crawl_myip(ips, many=False):
    url = 'https://myip.ms'
    ip_input_path = '//*[@id="home_txt"]'
    submit_butt_path = '//*[@id="home_submit"]'
    robo_test = '//*[@id="captcha_submit"]'

    options = Options()
    options.set_preference('dom.webnotifications.enabled', False)

    web = webdriver.Firefox(options=options)

    with web as driver:
        wait = WebDriverWait(driver, timeout=10)
        driver.get(url)
        wait.until(presence_of_element_located((By.XPATH, ip_input_path)))
        wait.until(presence_of_element_located((By.XPATH, submit_butt_path)))

        ip_box = driver.find_element(By.XPATH, ip_input_path)
        submit_button = driver.find_element(By.XPATH, submit_butt_path)

        if many:
            assert isinstance(ips, list)
            for ip in ips:
                ip_box.send_keys(ip)
                submit_button.click()
                try:
                    driver.find_element(By.XPATH, robo_test).click()
                except:
                    pass
                # call ip_data_store
                sleep(3)
        else:
            ip_box.send_keys(ips)
            submit_button.click()
            return  # ip data store


@shared_task
def crawl_ripe(ips, many=False):
    url = 'https://www.ripe.net'
    ip_input_path = '//*[@id="searchtext"]'
    submit_butt_path = '/html/body/header/div/div/div[3]/div[1]/div/div[1]/form/div/button'

    options = Options()
    options.set_preference('dom.webnotifications.enabled', False)

    web = webdriver.Firefox(options=options)

    with web as driver:
        wait = WebDriverWait(driver, timeout=10)
        driver.get(url)
        wait.until(presence_of_element_located((By.XPATH, ip_input_path)))
        wait.until(presence_of_element_located((By.XPATH, submit_butt_path)))

        ip_box = driver.find_element(By.XPATH, ip_input_path)
        submit_button = driver.find_element(By.XPATH, submit_butt_path)

        if many:
            assert isinstance(ips, list)
            for ip in ips:
                ip_box.send_keys(ip)
                submit_button.click()
                # call ip_data_store
                sleep(3)
        else:
            ip_box.send_keys(ips)
            submit_button.click()
            return  # ip data store
