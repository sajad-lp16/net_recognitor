from time import sleep
import pyperclip
import requests

from fake_headers import Headers
from django.conf import settings

from celery import shared_task
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    text_to_be_present_in_element,
    element_to_be_clickable,
)
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
        ip = settings.PROXY_IP_ADDRESS
        header = Headers(browser="chrome", os="linux", headers=False)
        custom_user_agent = header.generate()["User-Agent"]

        chrome_options = Options()

        chrome_options.add_argument("--proxy-server=http://" + ip)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"user-agent={custom_user_agent}")
        feature = DesiredCapabilities.CHROME
        feature["pageLoadStrategy"] = "none"
        driver = webdriver.Chrome(desired_capabilities=feature, options=chrome_options)
        driver.maximize_window()
        return driver

    @property
    def driver(self):
        return self._get_driver()


class BaseCrawler:
    def __init__(self, **kwargs):
        self.url = kwargs.get("url")
        self.manager_obj = kwargs.get("manager")
        self.driver_obj = BaseDriver()
        self._email = settings.AUTH_EMAIL_ADDRESS
        self._email_password = settings.AUTH_EMAIL_PASSWORD

    def crawl(self, ips, many):
        raise NotImplementedError

    def _login_crawl(self, ips, many):
        raise NotImplementedError

    def _no_login_crawl(self, ips, many):
        raise NotImplementedError


# --------------------------------------------Crawlers ----------------------------------------------------------


class IPInfoCrawler(BaseCrawler):
    def __init__(self, url):

        # login values ------------------------------------------------------------------------------------------
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

        self.data_target_source = '//*[@id="app"]/div/div[2]/div[2]/div'

        # no login values ---------------------------------------------------------------------------------------
        self.ip_input_path_n_login = '//*[@id="tryit-form"]/input'
        self.submit_butt_path_n_login = (
            "/html/body/div[1]/div/main/section[1]/div/div[2]/div/div[1]/form/button"
        )
        self.data_target_n_login = (
            '//*[@id="__next"]/div/main/section[1]/div/div[2]/div'
        )
        super().__init__(url=url, manager=data_managers.IPInfoManager())

    def crawl(self, ips, many=False):
        instance = self._no_login_crawl(ips, many)
        if instance is None:
            instance = self._login_crawl(ips, many)
        return instance

    def _login_crawl(self, ips, many=False):
        web = self.driver_obj.driver
        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            wait.until(presence_of_element_located((By.XPATH, self.login_url_path)))
            sleep(3)
            driver.execute_script("window.stop();")
            element = driver.find_element(By.XPATH, self.login_url_path)
            driver.execute_script("arguments[0].click();", element)
            wait.until(presence_of_element_located((By.XPATH, self.email_input_path)))
            sleep(3)
            driver.execute_script("window.stop();")
            driver.find_element(By.XPATH, self.email_input_path).send_keys(self._email)
            driver.find_element(By.XPATH, self.password_input_path).send_keys(
                self._email_password
            )
            driver.find_element(By.XPATH, self.login_butt_path).click()
            wait.until(presence_of_element_located((By.XPATH, self.ip_input_path)))
            sleep(2)
            driver.execute_script("window.stop();")
            ip_box = driver.find_element(By.XPATH, self.ip_input_path)
            wait.until(presence_of_element_located((By.XPATH, self.submit_butt_path)))
            wait.until(presence_of_element_located((By.XPATH, self.ip_input_path)))
            sleep(2)
            driver.execute_script("window.stop();")
            if not many:
                ip_box.send_keys(ips)
                sleep(8)
                wait.until(
                    presence_of_element_located((By.XPATH, self.data_target_source))
                )
                data_source = driver.find_element(
                    By.XPATH, self.data_target_source
                ).text
                return self.manager_obj.login_manager(data_source)

            assert isinstance(ips, list)
            for ip in ips:
                ip_box.send_keys(ip)
                sleep(2)
                self.manager_obj.login_manager(pyperclip.paste())
                sleep(1)

    def _no_login_crawl(self, ips, many=False):

        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            sleep(8)
            wait.until(
                presence_of_element_located((By.XPATH, self.ip_input_path_n_login))
            )
            wait.until(
                presence_of_element_located((By.XPATH, self.submit_butt_path_n_login))
            )

            ip_box = driver.find_element(By.XPATH, self.ip_input_path_n_login)
            submit_button = driver.find_element(By.XPATH, self.submit_butt_path_n_login)

            if many:
                assert isinstance(ips, list)
                for ip in ips:
                    ip_box.clear()
                    ip_box.send_keys(ip)
                    submit_button.click()
                    wait.until(
                        text_to_be_present_in_element(
                            (By.XPATH, self.data_target_n_login), ip
                        )
                    )
                    data_source = driver.find_element(
                        By.XPATH, self.data_target_n_login
                    ).text
                    self.manager_obj.no_login_manager(data_source)
                    sleep(2)
            else:
                ip_box.clear()
                ip_box.send_keys(ips)
                submit_button.click()
                wait.until(
                    text_to_be_present_in_element(
                        (By.XPATH, self.data_target_n_login), ips
                    )
                )
                data_source = driver.find_element(
                    By.XPATH, self.data_target_n_login
                ).text
                return self.manager_obj.no_login_manager(data_source)


class MyIpCrawler(BaseCrawler):
    def __init__(self, url):

        # login values ------------------------------------------------------------------------------------------
        self.ip_input_path = '//*[@id="global_txt"]'
        self.submit_butt_path = '//*[@id="global_submit"]'
        self.login_button_path = "/html/body/div[1]/div/table/tbody/tr/td/table[1]/tbody/tr/td[2]/div[2]/span[2]/a[1]"
        self.robo_test = '//*[@id="captcha_submit"]'
        self.login_submit_button_class_name = "ui-button-text"
        self.dialog_id = "uidialog"

        # no login values ---------------------------------------------------------------------------------------
        self.ip_input_path_n_login = '//*[@id="home_txt"]'
        self.submit_butt_path_n_login = '//*[@id="home_submit"]'

        super().__init__(url=url, manager=data_managers.MyIPManager())

    def crawl(self, ips, many=False):
        instance = self._no_login_crawl(ips, many)
        if instance is None:
            instance = self._login_crawl(ips, many)
        return instance

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
            dialog.find_element(By.ID, "email").send_keys(self._email)
            dialog.find_element(By.ID, "password").send_keys(self._email_password)

            dialog.find_element(
                By.CLASS_NAME, self.login_submit_button_class_name
            ).click()
            sleep(1)
            wait.until(presence_of_element_located((By.XPATH, self.robo_test)))
            sleep(2)

            for _ in range(10):
                try:
                    driver.find_element(By.XPATH, self.robo_test).click()
                except:
                    pass
                sleep(0.5)

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
                    for _ in range(10):
                        try:
                            driver.find_element(By.XPATH, self.robo_test).click()
                        except:
                            pass
                        sleep(0.5)
                    sleep(3)
            else:
                ip_box.send_keys(ips)
                submit_button.click()
                sleep(4)
                for _ in range(10):
                    try:
                        driver.find_element(By.XPATH, self.robo_test).click()
                    except:
                        pass
                    sleep(0.5)
                sleep(3)
                return self.manager_obj.login_manager(driver.page_source)

    def _no_login_crawl(self, ips, many=False):
        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            wait.until(
                presence_of_element_located((By.XPATH, self.ip_input_path_n_login))
            )
            wait.until(
                presence_of_element_located((By.XPATH, self.submit_butt_path_n_login))
            )
            ip_input_box = driver.find_element(By.XPATH, self.ip_input_path_n_login)
            submit_button = driver.find_element(By.XPATH, self.submit_butt_path_n_login)
            if many:
                assert isinstance(ips, list)
                for ip in ips:
                    ip_input_box.send_keys(ip)
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
                ip_input_box.send_keys(ips)
                submit_button.click()
                sleep(4)
                for _ in range(10):
                    try:
                        driver.find_element(By.XPATH, self.robo_test).click()
                    except:
                        pass
                    sleep(0.5)
                sleep(2)
                return self.manager_obj.login_manager(driver.page_source)


class IPDataCrawler(BaseCrawler):
    def __init__(self, url):
        # shared values -----------------------------------------------------------------------------------------
        self.payload = {"api-key": settings.IP_DATA_TOKEN}
        self.api_url = settings.CRAWL_SOURCES.get("ipdata").get("api")

        # login values ------------------------------------------------------------------------------------------
        self.login_link_path = "/html/body/nav/div/div/a[1]"
        self.data_target_path = "/html/body/div[1]/div[2]/div/div"
        self.email_input_path = '//*[@id="email"]'
        self.password_input_path = '//*[@id="password"]'
        self.demo_ip_search_link_path = "/html/body/nav/div/div[2]/ul[1]/li[2]/a"
        self.login_submit_path = '//*[@id="submit"]'
        self.login_ip_input_path = '//*[@id="searchIP"]'

        # no login values ---------------------------------------------------------------------------------------
        self.ip_input_path_n_login = "//*[@id='searchIP']"
        self.submit_button_path_n_login = '//*[@id="searchIPButton"]'
        self.data_target_path_n_login = '//*[@id="demo"]'

        super().__init__(url=url, manager=data_managers.IPDataManager())

    def crawl(self, ips, many=False):
        instance = self._login_api_crawl(ips, many)
        if instance is None:
            instance = self._no_login_crawl(ips, many)
        if instance is None:
            instance = self._login_crawl(ips, many)
        return instance

    def _login_crawl(self, ips, many):
        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            wait.until(presence_of_element_located((By.XPATH, self.login_link_path)))
            element = driver.find_element(By.XPATH, self.login_link_path)
            driver.execute_script("arguments[0].click();", element)
            wait.until(presence_of_element_located((By.XPATH, self.email_input_path)))
            wait.until(
                presence_of_element_located((By.XPATH, self.password_input_path))
            )
            wait.until(element_to_be_clickable((By.XPATH, self.login_submit_path)))
            email_elem = driver.find_element(By.XPATH, self.email_input_path)
            password_elem = driver.find_element(By.XPATH, self.password_input_path)
            login_button_elem = driver.find_element(By.XPATH, self.login_submit_path)

            email_elem.send_keys(self._email)
            password_elem.send_keys(self._email_password)
            login_button_elem.click()
            sleep(3)
            for _ in range(5):
                try:
                    driver.find_element(By.XPATH, self.email_input_path).send_keys(
                        self._email
                    )
                    driver.find_element(By.XPATH, self.password_input_path).send_keys(
                        self._email_password
                    )
                    sleep(3)
                    driver.find_element(By.XPATH, self.login_submit_path).click()
                    sleep(2)
                except:
                    sleep(5)
                    pass
            wait.until(
                presence_of_element_located((By.XPATH, self.demo_ip_search_link_path))
            )
            driver.find_element(By.XPATH, self.demo_ip_search_link_path).click()
            sleep(4)
            wait.until(
                presence_of_element_located((By.XPATH, self.login_ip_input_path))
            )
            ip_input_box = driver.find_element(By.XPATH, self.login_ip_input_path)
            if many:
                pass

            else:
                ip_input_box.send_keys(ips)
                ip_input_box.send_keys(Keys.ENTER)
                wait.until(
                    text_to_be_present_in_element(
                        (By.XPATH, self.data_target_path), "IP"
                    )
                )
                sleep(2)
                source = driver.find_element(By.XPATH, self.data_target_path).text
                return self.manager_obj.login_manager(source)

    def _login_api_crawl(self, ips, many):
        if many:
            assert isinstance(ips, list)
            for ip in ips:
                data = requests.get(self.api_url + ip, params=self.payload).json()
                self.manager_obj.login_manager(data)
        else:
            data = requests.get(self.api_url + ips, params=self.payload).json()
            return self.manager_obj.login_api_manager(data)

    def _no_login_crawl(self, ips, many):
        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            wait.until(
                presence_of_element_located((By.XPATH, self.submit_button_path_n_login))
            )
            wait.until(
                presence_of_element_located((By.XPATH, self.ip_input_path_n_login))
            )
            ip_input_box = driver.find_element(By.XPATH, self.ip_input_path_n_login)
            submit_button_path = driver.find_element(
                By.XPATH, self.submit_button_path_n_login
            )
            sleep(2)
            if many:
                assert isinstance(ips, list)
                for ip in ips:
                    ip_input_box.send_keys(ip)
                    submit_button_path.click()
                    sleep(3)
            else:
                ip_input_box.send_keys(ips)
                sleep(2)
                submit_button_path.click()
                wait.until(
                    text_to_be_present_in_element(
                        (By.XPATH, self.data_target_path_n_login), "ip"
                    )
                )
                source = driver.find_element(
                    By.XPATH, self.data_target_path_n_login
                ).text
                return self.manager_obj.no_login_manager(source)


class RipeCrawler(BaseCrawler):
    def __init__(self, url, **kwargs):

        # login values ---------------------------------------------------------------------------------------
        self.login_url = kwargs.get("login_url")
        self.login_button_path = '//*[@id="main"]/svg'
        self.email_input_path = "/html/body/div/div[1]/form/label[1]/input"
        self.password_input_path = "/html/body/div/div[1]/form/label[2]/input"
        self.submit_login_button_path = "/html/body/div/div[1]/form/button"

        self.target_source_data = (
            "/html/body/app-db-web-ui/main/div/section[2]/div[1]/query/div"
        )

        self.second_ip_input_path = '//*[@id="queryStringInput"]'
        self.second_submit_button_path = "/html/body/app-db-web-ui/main/div/section[2]/div[1]/query/section/form/div[1]/div[1]/mat-form-field/div/div[1]/div[2]/button/span[1]/mat-icon"

        # no login values ---------------------------------------------------------------------------------------
        self.api_url_n_login = settings.CRAWL_SOURCES.get("ripe").get("api")
        self.data_target_n_login = '//*[@id="resultsSection"]/div'
        self.ip_input_path_n_login = '//*[@id="searchtext"]'
        self.submit_butt_path_n_login = (
            "/html/body/header/div/div/div[3]/div[1]/div/div[1]/form/div/button"
        )
        self.initial_ip_input_path = '//*[@id="searchtext"]'
        self.initial_submit_button_path = (
            "/html/body/header/div/div/div[3]/div[1]/div/div[1]/form/div/button"
        )

        super().__init__(url=url, manager=data_managers.RipeManager())

    def crawl(self, ips, many=False):
        instance = self._no_login_api(ips, many)
        if instance is None:
            instance = self._no_login_crawl(ips, many)
        if instance is None:
            instance = self._login_crawl(ips, many)
        return instance

    def _no_login_crawl(self, ips, many=False):
        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(self.url)
            wait.until(
                presence_of_element_located((By.XPATH, self.ip_input_path_n_login))
            )
            wait.until(
                presence_of_element_located((By.XPATH, self.submit_butt_path_n_login))
            )

            initial_ip_box = driver.find_element(By.XPATH, self.ip_input_path_n_login)
            initial_submit_button = driver.find_element(
                By.XPATH, self.submit_butt_path_n_login
            )

            if not many:
                initial_ip_box.send_keys(ips)
                initial_submit_button.click()
                sleep(2)
                wait.until(
                    presence_of_element_located((By.XPATH, self.data_target_n_login))
                )
                data_target = driver.find_element(
                    By.XPATH, self.data_target_n_login
                ).text
                return self.manager_obj.no_login_manager(data_target)

            assert isinstance(ips, list)
            initial_ip_box.send_keys(ips.pop(0))
            initial_submit_button.click()
            wait.until(
                text_to_be_present_in_element(
                    (By.XPATH, self.target_source_data), "inetnum"
                )
            )
            source_data = driver.find_element(By.XPATH, self.target_source_data).text
            self.manager_obj.login_manager(source_data)
            wait.until(
                presence_of_element_located((By.XPATH, self.second_ip_input_path))
            )
            wait.until(
                presence_of_element_located((By.XPATH, self.second_submit_button_path))
            )

            second_ip_input = driver.find_element(By.XPATH, self.second_ip_input_path)
            second_submit_button = driver.find_element(
                By.XPATH, self.second_submit_button_path
            )

            for ip in ips:
                second_ip_input.send_keys(ip)
                second_submit_button.click()
                wait.until(
                    text_to_be_present_in_element(
                        (By.XPATH, self.target_source_data), "inetnum"
                    )
                )
                source_data = driver.find_element(
                    By.XPATH, self.target_source_data
                ).text
                self.manager_obj.login_manager(source_data)
                sleep(3)

    def _login_crawl(self, ips, many=False):
        web = self.driver_obj.driver

        with web as driver:
            wait = WebDriverWait(driver, timeout=settings.DRIVER_TIMEOUT)
            driver.get(
                self.login_url
            )  # That iss because the login url svg was un reachable
            wait.until(presence_of_element_located((By.XPATH, self.email_input_path)))
            wait.until(
                presence_of_element_located((By.XPATH, self.password_input_path))
            )
            sleep(2)
            driver.execute_script("window.stop();")
            driver.find_element(By.XPATH, self.email_input_path).send_keys(self._email)
            driver.find_element(By.XPATH, self.password_input_path).send_keys(
                self._email_password
            )
            sleep(1)
            driver.find_element(By.XPATH, self.submit_login_button_path).click()
            sleep(2)
            wait.until(
                presence_of_element_located((By.XPATH, self.initial_ip_input_path))
            )
            wait.until(
                presence_of_element_located((By.XPATH, self.initial_submit_button_path))
            )
            sleep(2)
            driver.execute_script("window.stop();")
            initial_ip_input = driver.find_element(By.XPATH, self.initial_ip_input_path)
            initial_submit_button = driver.find_element(
                By.XPATH, self.initial_submit_button_path
            )

            if not many:
                initial_ip_input.send_keys(ips)
                initial_submit_button.click()
                wait.until(
                    text_to_be_present_in_element(
                        (By.XPATH, self.target_source_data), "inetnum"
                    )
                )
                source_data = driver.find_element(
                    By.XPATH, self.target_source_data
                ).text
                return self.manager_obj.login_manager(source_data)

            assert isinstance(ips, list)
            initial_ip_input.send_keys(ips.pop(0))
            initial_submit_button.click()
            wait.until(
                text_to_be_present_in_element(
                    (By.XPATH, self.target_source_data), "inetnum"
                )
            )
            source_data = driver.find_element(By.XPATH, self.target_source_data).text
            self.manager_obj.login_manager(source_data)
            wait.until(
                presence_of_element_located((By.XPATH, self.second_ip_input_path))
            )
            wait.until(
                presence_of_element_located((By.XPATH, self.second_submit_button_path))
            )
            second_ip_input = driver.find_element(By.XPATH, self.second_ip_input_path)
            second_submit_button = driver.find_element(
                By.XPATH, self.second_submit_button_path
            )
            for ip in ips:
                second_ip_input.send_keys(ip)
                second_submit_button.click()
                wait.until(
                    text_to_be_present_in_element(
                        (By.XPATH, self.target_source_data), "inetnum"
                    )
                )
                source_data = driver.find_element(
                    By.XPATH, self.target_source_data
                ).text
                self.manager_obj.login_manager(source_data)
                sleep(3)

    def _no_login_api(self, ips, many=False):
        if many:
            assert isinstance(ips, list)
            for ip in ips:
                payload = {"query-string": ip, "source": "RIPE"}
                data = requests.get(self.api_url_n_login, params=payload).json()
                self.manager_obj.no_login_api_manager(data)
        else:
            payload = {"query-string": ips, "source": "RIPE"}
            data = requests.get(self.api_url_n_login, params=payload).json()
            return self.manager_obj.no_login_api_manager(data)


# --------------------------------------------- Tasks ----------------------------------------------------------


@shared_task
def crawl_ripe(ips, many=False):
    source_url = settings.CRAWL_SOURCES.get("ripe").get("main")
    login_url = settings.CRAWL_SOURCES.get("ripe").get("login")
    if source_url is None:
        return
    crawler = RipeCrawler(source_url, login_url=login_url)
    return crawler.crawl(ips, many)


@shared_task
def crawl_my_ip(ips, many=False):
    source_url = settings.CRAWL_SOURCES.get("myip").get("main")
    if source_url is None:
        return
    crawler = MyIpCrawler(source_url)
    return crawler.crawl(ips, many)


@shared_task
def crawl_ip_info(ips, many=False):
    source_url = settings.CRAWL_SOURCES.get("ipinfo").get("main")
    if source_url is None:
        return
    crawler = IPInfoCrawler(source_url)
    return crawler.crawl(ips, many)


@shared_task
def crawl_ip_data(ips, many=False):
    source_url = settings.CRAWL_SOURCES.get("ipdata").get("main")
    if source_url is None:
        return
    crawler = IPDataCrawler(source_url)
    return crawler.crawl(ips, many)
