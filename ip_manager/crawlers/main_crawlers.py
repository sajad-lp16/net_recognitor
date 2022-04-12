from time import sleep
import pyperclip

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
    url = "https://ipinfo.io/"
    email = "s.dagh.20.hd.hd@gmail.com"
    password = "Aa@123456"
    email_input_path = "/html/body/div/div/div/div/form/div[2]/input"
    password_input_path = "/html/body/div[1]/div/div/div/form/div[3]/input"
    login_url_path = "/html/body/header/nav/div/div/ul[1]/li[1]/a"
    login_butt_path = "/html/body/div[1]/div/div/div/form/button"
    ip_input_path = "/html/body/div[1]/div/div[2]/div[1]/input"
    submit_butt_path = "/html/body/div[1]/div/div[2]/div[1]/div/button[4]"
    json_data_button = (
        "/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div/div[2]/button"
    )
    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)

    web = webdriver.Firefox(options=options)

    with web as driver:
        wait = WebDriverWait(driver, timeout=15)
        driver.get(url)
        wait.until(presence_of_element_located((By.XPATH, login_url_path)))
        driver.find_element(By.XPATH, login_url_path).click()
        wait.until(presence_of_element_located((By.XPATH, email_input_path)))
        driver.find_element(By.XPATH, email_input_path).send_keys(email)
        driver.find_element(By.XPATH, password_input_path).send_keys(password)
        driver.find_element(By.XPATH, login_butt_path).click()
        wait.until(presence_of_element_located((By.XPATH, ip_input_path)))
        ip_box = driver.find_element(By.XPATH, ip_input_path)
        wait.until(presence_of_element_located((By.XPATH, submit_butt_path)))
        wait.until(presence_of_element_located((By.XPATH, ip_input_path)))
        if many:
            assert isinstance(ips, list)
            for ip in ips:
                ip_box.send_keys(ip)
                sleep(2)
                data_managers.ip_info_manager(pyperclip.paste())
                sleep(1)
        else:
            ip_box.send_keys(ips)
            sleep(2)
            driver.find_element(By.XPATH, json_data_button).click()
            return data_managers.ip_info_manager(pyperclip.paste())


@shared_task
def crawl_ip_registry(ips, many=False):
    url = "https://ipregistry.co/"
    ip_input_path = '//*[@id="iptocheck"]'
    submit_butt_path = '//*[@id="ipcheck_submit"]'

    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)

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
    url = "https://ipdata.co/"
    ip_input_path = '//*[@id="searchIP"]'
    submit_butt_path = '//*[@id="searchIPButton"]'

    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)

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
    url = "https://myip.ms"
    ip_input_path = '//*[@id="home_txt"]'
    submit_butt_path = '//*[@id="home_submit"]'
    robo_test = '//*[@id="captcha_submit"]'

    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)

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
    url = "https://www.ripe.net"
    ip_input_path = '//*[@id="searchtext"]'
    submit_butt_path = (
        "/html/body/header/div/div/div[3]/div[1]/div/div[1]/form/div/button"
    )

    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)

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
