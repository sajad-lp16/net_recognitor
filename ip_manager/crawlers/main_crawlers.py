from time import sleep
import pyperclip
import requests

from django.conf import settings

from celery import shared_task
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait

from . import data_managers


# ----------------------------------------- Base_Classes --------------------------------------------------------
class BaseDriver:
    __instance = {}

    def __new__(cls, *args, **kwargs):
        if BaseDriver.__instance.get(cls) is None:
            BaseDriver.__instance[cls] = super().__new__(cls, *args, **kwargs)
        return BaseDriver.__instance[cls]

    @staticmethod
    def _get_driver():
        feature = DesiredCapabilities.CHROME
        feature["pageLoadStrategy"] = "none"
        driver = webdriver.Chrome(desired_capabilities=feature)
        driver.maximize_window()
        return driver

    @property
    def driver(self):
        return self._get_driver()


class BaseCrawler:
    def __init__(self, **kwargs):
        self.url = kwargs.get("url")
        self.driver_obj = BaseDriver()

    def crawl(self, ips, many):
        raise NotImplementedError

    def _login_crawl(self, ips, many):
        raise NotImplementedError

    def _no_login_crawl(self, ips, many):
        raise NotImplementedError


# --------------------------------------------Crawlers ----------------------------------------------------------


class IPInfoCrawler(BaseCrawler):
    def __init__(self, url):
        self.url = url
        self.email = settings.AUTH_EMAIL_ADDRESS
        self.password = settings.AUTH_EMAIL_PASSWORD
        self.email_input_path = "/html/body/div/div/div/div/form/div[2]/input"
        self.password_input_path = "/html/body/div[1]/div/div/div/form/div[3]/input"
        self.login_url_path = (
            '//*[@id="__next"]/div/header/nav/div[1]/div[5]/div[2]/a[1]'
        )
        self.login_butt_path = "/html/body/div[1]/div/div/div/form/button"
        self.ip_input_path = "/html/body/div[1]/div/div[2]/div[1]/input"
        self.submit_butt_path = "/html/body/div[1]/div/div[2]/div[1]/div/button[4]"
        self.json_data_button = (
            "/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div/div[2]/button"
        )
        self.ip_input_path_n_login = '//*[@id="homepage-search-input"]'
        self.submit_butt_path_n_login = (
            "/html/body/div[1]/div[1]/div/div/div/div/div/div[3]/div/div[1]/button"
        )
        self.data_target = '//*[@id="ipw_main_area"]'
        self.manager_obj = data_managers.IPInfoManager()
        super().__init__(url=url)

    def crawl(self, ips, many):
        return self._login_crawl(ips, many)

    def _login_crawl(self, ips, many=False):
        web = self.driver_obj.driver
        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            wait.until(presence_of_element_located((By.XPATH, self.login_url_path)))
            driver.execute_script("window.stop();")
            driver.find_element(By.XPATH, self.login_url_path).click()
            wait.until(presence_of_element_located((By.XPATH, self.email_input_path)))
            driver.execute_script("window.stop();")
            driver.find_element(By.XPATH, self.email_input_path).send_keys(self.email)
            driver.find_element(By.XPATH, self.password_input_path).send_keys(
                self.password
            )
            driver.find_element(By.XPATH, self.login_butt_path).click()
            wait.until(presence_of_element_located((By.XPATH, self.ip_input_path)))
            driver.execute_script("window.stop();")
            ip_box = driver.find_element(By.XPATH, self.ip_input_path)
            wait.until(presence_of_element_located((By.XPATH, self.submit_butt_path)))
            wait.until(presence_of_element_located((By.XPATH, self.ip_input_path)))
            driver.execute_script("window.stop();")
            if many:
                assert isinstance(ips, list)
                for ip in ips:
                    ip_box.send_keys(ip)
                    sleep(2)
                    self.manager_obj.login_manager(pyperclip.paste())
                    sleep(1)
            else:
                ip_box.send_keys(ips)
                sleep(2)
                driver.find_element(By.XPATH, self.json_data_button).click()
                return self.manager_obj.login_manager(pyperclip.paste())

    def _no_login_crawl(self, ips, many=False):

        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=10)
            driver.get(self.url)
            wait.until(
                presence_of_element_located((By.XPATH, self.ip_input_path_n_login))
            )
            wait.until(
                presence_of_element_located((By.XPATH, self.submit_butt_path_n_login))
            )

            ip_box = driver.find_element(By.XPATH, self.ip_input_path_n_login)
            submit_button = driver.find_element(By.XPATH, self.ip_input_path_n_login)

            if many:
                assert isinstance(ips, list)
                for ip in ips:
                    ip_box.send_keys(ip)
                    submit_button.click()
                    data_source = driver.find_element(By.XPATH, self.data_target).text
                    self.manager_obj.login_manager(data_source)
                    sleep(2)
            else:
                ip_box.send_keys(ips)
                submit_button.click()
                sleep(2)
                data_source = driver.find_element(By.XPATH, self.data_target).text
                return self.manager_obj.login_manager(data_source)


class MyIpCrawler(BaseCrawler):
    def __init__(self, url):
        self.url = "https://myip.ms"
        self.ip_input_path = '//*[@id="global_txt"]'
        self.submit_butt_path = '//*[@id="global_submit"]'
        self.login_button_path = "/html/body/div[1]/div/table/tbody/tr/td/table[1]/tbody/tr/td[2]/div[2]/span[2]/a[1]"
        self.robo_test = '//*[@id="captcha_submit"]'
        self.login_submit_button_class_name = "ui-button-text"
        self.dialog_id = "uidialog"
        self.manager = data_managers.MyIPManager()
        super().__init__(url=url)

    def crawl(self, ips, many=False):
        return self._login_crawl(ips, many)

    def _login_crawl(self, ips, many=False):
        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            wait.until(presence_of_element_located((By.XPATH, self.login_button_path)))
            sleep(2)
            driver.execute_script("window.stop();")
            driver.find_element(By.XPATH, self.login_button_path).click()
            wait.until(presence_of_element_located((By.ID, self.dialog_id)))
            sleep(2)
            dialog = driver.find_element(By.ID, self.dialog_id)
            dialog.find_element(By.ID, "email").send_keys(settings.AUTH_EMAIL_ADDRESS)
            dialog.find_element(By.ID, "password").send_keys(
                settings.AUTH_EMAIL_PASSWORD
            )

            dialog.find_element(
                By.CLASS_NAME, self.login_submit_button_class_name
            ).click()
            sleep(1)
            wait.until(presence_of_element_located((By.XPATH, self.robo_test)))
            sleep(4)
            driver.find_element(By.XPATH, self.robo_test).click()
            sleep(4)
            try:
                driver.find_element(By.XPATH, self.robo_test).click()
            except:
                pass

            wait.until(presence_of_element_located((By.XPATH, self.ip_input_path)))
            wait.until(presence_of_element_located((By.XPATH, self.submit_butt_path)))
            driver.execute_script("window.stop();")
            ip_box = driver.find_element(By.XPATH, self.ip_input_path)
            submit_button = driver.find_element(By.XPATH, self.submit_butt_path)
            if many:
                assert isinstance(ips, list)
                for ip in ips:
                    ip_box.send_keys(ip)
                    submit_button.click()
                    sleep(4)
                    try:
                        driver.find_element(By.XPATH, self.robo_test).click()
                        sleep(4)
                        driver.find_element(By.XPATH, self.robo_test).click()
                    except:
                        pass
                    sleep(3)
            else:
                ip_box.send_keys(ips)
                submit_button.click()
                sleep(4)
                try:
                    driver.find_element(By.XPATH, self.robo_test).click()
                    sleep(4)
                    driver.find_element(By.XPATH, self.robo_test).click()
                except:
                    pass
                return self.manager.login_manager(driver.page_source)

    def _no_login_crawl(self, ips, many=False):
        pass


class IPDataCrawler(BaseCrawler):
    def __init__(self, url):
        self.payload = {"api-key": settings.IP_DATA_TOKEN}
        self.path = settings.CRAWL_SOURCES.get("ipdata_api")
        self.manager_obj = data_managers.IPDataManager()
        super().__init__(url=url)

    def crawl(self, ips, many):
        pass

    def _login_crawl(self, ips, many):
        if many:
            assert isinstance(ips, list)
            for ip in ips:
                data = requests.get(self.path + ip, params=self.payload).json()
                self.manager_obj.login_manager(data)
        else:
            data = requests.get(self.path + ips, params=self.payload).json()
            return self.manager_obj.login_manager(data)

    def _no_login_crawl(self, ips, many):
        pass


class RipeCrawler(BaseCrawler):
    def __init__(self, url):
        self.ip_input_path = '//*[@id="searchtext"]'
        self.submit_butt_path = (
            "/html/body/header/div/div/div[3]/div[1]/div/div[1]/form/div/button"
        )
        super().__init__(url=url)

    def crawl(self, ips, many):
        pass

    def _no_login_crawl(self, ips, many=False):
        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            wait.until(presence_of_element_located((By.XPATH, self.ip_input_path)))
            wait.until(presence_of_element_located((By.XPATH, self.submit_butt_path)))

            ip_box = driver.find_element(By.XPATH, self.ip_input_path)
            submit_button = driver.find_element(By.XPATH, self.submit_butt_path)

            if many:
                assert isinstance(ips, list)
                for ip in ips:
                    ip_box.send_keys(ip)
                    submit_button.click()
                    sleep(3)
            else:
                ip_box.send_keys(ips)
                submit_button.click()
                return

    def _login_crawl(self, ips, many):
        pass


# --------------------------------------------- Tasks ----------------------------------------------------------


@shared_task
def crawl_ripe(ips, many=False):
    source_url = settings.CRAWL_SOURCES.get("ripe")
    if source_url is None:
        return
    crawler = RipeCrawler(source_url)
    return crawler.crawl(ips, many)


@shared_task
def crawl_my_ip(ips, many=False):
    source_url = settings.CRAWL_SOURCES.get("myip")
    if source_url is None:
        return
    crawler = MyIpCrawler(source_url)
    return crawler.crawl(ips, many)


@shared_task
def crawl_ip_info(ips, many=False):
    source_url = settings.CRAWL_SOURCES.get("ipinfo")
    if source_url is None:
        return
    crawler = IPInfoCrawler(source_url)
    return crawler.crawl(ips, many)


@shared_task
def crawl_ip_data(ips, many=False):
    source_url = settings.CRAWL_SOURCES.get("ipdata")
    if source_url is None:
        return
    crawler = IPDataCrawler(source_url)
    return crawler.crawl(ips, many)
