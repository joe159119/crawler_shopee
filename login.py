import os
import sys
import pickle
import logging
import datetime
import inspect
import csv
from time import gmtime, strftime, sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Config:

    DEBUG = False
    LOGGING_PATH = 'log'
    WAIT_TIMEOUT = 5
    elements_by_css = {
        "POP_MODAL": ".shopee-popup__close-btn",
        "AVATAR": ".shopee-avatar",
        "NAV_LOGIN_MODAL": ".navbar__link--account",
        "LOGIN_FAILED": ".shopee-authen .shopee-authen__error"
    }
    elements_by_name = {
        "LOGIN_USER": "loginKey",
        "LOGIN_PASS": "password"
    }
    elements_by_text = {
        "NAV_LOGIN_MODAL": "//div/ul/a[contains(., '登入')]",
        "LOGIN_SUBMIT": "//button[text()=\"登入\"]",
        "SMS_MODAL": "//div[contains(., '請輸入驗證碼')]",
        "SMS_TEXT": "//input[contains(@autocomplete, 'one-time-code')]",
        "SMS_SUBMIT": "//button[contains(., '驗證') or contains(., '認證')]",
        "COIN_PAGE_READY": "//main/section/div/div[text()=\"蝦幣獎勵\"]",
        "GET_COIN": "//main/section/div/button",
        "COIN_NOW": "//main/section/div/a/p",
        "COIN_REGULAR": "//button[contains(., '明天再回來領取')]"
    }
    urls = {
        "INDEX": "https://shopee.tw",
        "COIN_PAGE": "https://shopee.tw/shopee-coins"
    }
    path = os.path.dirname(os.path.abspath(__file__))


class Logger(Config):
    def __init__(self):
        path = os.path.join(self.path, self.LOGGING_PATH)
        if not os.path.exists(path):
            os.makedirs(path)
        path = "{}/{}".format(path,
                              datetime.datetime.now().strftime("shopee.%Y-%m.log"))
        logging_level = logging.DEBUG if self.DEBUG else logging.INFO
        logger = logging.getLogger()
        logger.setLevel(logging_level)
        formatter = logging.Formatter(
            '[%(filename)s:%(lineno)s - %(funcName)20s() ] %(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        fh = logging.FileHandler(path)
        fh.setFormatter(formatter)
        logger.addHandler(ch)
        logger.addHandler(fh)
        self.logger = logger

    def get_logger(self):
        return self.logger


logger = Logger().get_logger()


class Driver(Config):

    def __init__(self, width, height):

        chrome_options = Options()

        # if not self.DEBUG or self.path == '/code':
        #     # chrome_options.add_experimental_option("detach", True)
        #     chrome_options.add_argument('--headless')
        #     chrome_options.add_argument('--start-maximized')
        #     chrome_options.add_argument('disable-infobars')
        #     chrome_options.add_argument('--disable-extensions')
        #     chrome_options.add_argument('--no-sandbox')
        #     chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('chromedriver', options=chrome_options)
        self.driver.set_window_size(width, height)
        self.path = os.path.dirname(os.path.abspath(__file__))
        print("Init driver done.")

    def saveCookie(self, cookieName):
        with open(self.path + '/cookies/' + cookieName, 'wb') as filehandler:
            pickle.dump(self.driver.get_cookies(), filehandler)
        logger.info("Save cookie to {}".format(cookieName))

    def loadCookie(self, cookieName):
        with open(self.path + '/cookies/' + cookieName, 'rb') as cookiesfile:
            for cookie in pickle.load(cookiesfile):
                self.driver.add_cookie(cookie)

    def getRequest(self, url):
        self.driver.get(self.urls.get(url))

    def wait_until(self, method=None, target=None):
        if method == 'css':
            selector = By.CSS_SELECTOR
            target = self.elements_by_css.get(target)

        if method == 'text':
            selector = By.XPATH
            target = self.elements_by_text.get(target)

        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.presence_of_element_located((selector, target))
        )

    def find(self, method=None, target=None):
        if method == 'css':
            target = self.elements_by_css.get(target)
            result = self.driver.find_elements_by_css_selector(target)
        if method == 'name':
            target = self.elements_by_name.get(target)
            result = self.driver.find_elements_by_name(target)
        if method == 'text':
            target = self.elements_by_text.get(target)
            result = self.driver.find_elements_by_xpath(target)

        try:
            logger.debug(result[0])
        except:
            logger.debug(result)

        return result[0] if len(result) is 1 else result

    def get_userlist_csv(self):
        userlist = []
        with open('env.csv', newline='') as csvfile:

            rows = csv.reader(csvfile)

            for row in rows:
                userlist.append(row)

        return userlist


class Crawler(Driver, Config):

    def __init__(self):
        super().__init__(1200, 800)

    def checkPopModal(self):
        try:
            sleep(3)
            pop = self.find("css", "POP_MODAL")
            pop.click()
            logger.info("pop modal close")
        except:
            logger.info("pop modal not found")

    def checkLogin(self):
        try:
            self.wait_until("css", "AVATAR")
            logger.info("Login Success")
            return True
        except Exception as e:
            logger.info("Login Failed")
            return False

    def loginByPass(self, username, password):
        try:
            login_page_url = self.find(
                "text", "NAV_LOGIN_MODAL").get_attribute('href')
            self.driver.get(login_page_url)
            self.wait_until("text", "LOGIN_SUBMIT")
        except Exception as e:
            logger.error("Login Modal not showing"+repr(e))
            self.close()
        try:
            # Enter Account & Password
            accountText = self.find("name", "LOGIN_USER")
            passwordText = self.find("name", "LOGIN_PASS")
            submitButtom = self.find("text", "LOGIN_SUBMIT")

            accountText.send_keys(username)
            passwordText.send_keys(password)

            logger.info("Use password to login. Wait SMS for 10 seconds...")
            logger.info(
                "You need to click login button manually and complete the login validation.")
            sleep(10)
            input('Press any key to continue.')

        except Exception as e:
            logger.error("Wrong account and password"+repr(e))
            self.close()
            sys.exit(0)

    def run(self):
        self.getRequest("INDEX")
        self.checkPopModal()
        logger.info("You need to input user information in console.")
        username = input('username: ')
        password = input('password: ')
        self.loginByPass(username, password)
        if not self.checkLogin():
            sleep(3)
            logger.info(
                "Enter the SMS and click button to send it. Wait 3 seconeds...")
            sleep(3)
            input('Press any key to continue.')
            if not self.checkLogin():
                self.close()
                logger.error(
                    "Login Failed. Your account or password seems to be wrong.")
        cookie_name = username + '.pkl'
        self.saveCookie(cookie_name)
        self.close()

    def close(self):
        self.driver.close()
        logger.info("driver close")


if __name__ == "__main__":
    Crawler().run()
    logger.info("Program exit")
    sys.exit(0)
