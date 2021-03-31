import os
import sys
import pickle
import logging
import datetime
import inspect
from env import *
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
        "LOGIN_SUBMIT": "//button[text()=\"登入\"]",
        "SMS_MODAL": "//div[contains(., '請輸入驗證碼')]",
        "SMS_TEXT": "//input[contains(@type, 'tel')]",
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

        if not self.DEBUG or self.path == '/code':
            # chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('disable-infobars')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('chromedriver', options=chrome_options)
        self.driver.set_window_size(width, height)
        self.path = os.path.dirname(os.path.abspath(__file__))
        print("Init driver done.")

    def saveCookie(self, cookieName):
        with open(self.path + '/' + cookieName, 'wb') as filehandler:
            pickle.dump(self.driver.get_cookies(), filehandler)
        logger.info("Save cookie to {}".format(cookieName))

    def loadCookie(self, cookieName):
        with open(self.path + '/' + cookieName, 'rb') as cookiesfile:
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

    def loginByCookie(self, cookieName):
        try:
            self.loadCookie(cookieName)
            self.driver.refresh()
            logger.info("Use {} to login".format(cookieName))
        except Exception as e:
            logger.info("{} not found".format(cookieName))

    def loginByPass(self):
        try:
            login_button = self.find("css", "NAV_LOGIN_MODAL")[1]
            login_button.click()
            self.wait_until("text", "LOGIN_SUBMIT")
        except Exception as e:
            logger.error("Login Modal not showing"+repr(e))
            self.close()
        try:
            # Enter Account & Password
            accountText = self.find("name", "LOGIN_USER")
            passwordText = self.find("name", "LOGIN_PASS")
            submitButtom = self.find("text", "LOGIN_SUBMIT")

            accountText.send_keys(text_username)
            passwordText.send_keys(text_password)

            count = 0
            while self.find("text", "LOGIN_SUBMIT") and count < 3:
                submitButtom.click()
                count += 1
                sleep(5)

            logger.info("Use password to login")
        except Exception as e:
            logger.error("Wrong account and password"+repr(e))
            self.close()
            sys.exit(0)

    def checkSMS(self):
        try:
            logger.info("wait_until SMS_MODAL")
            self.wait_until("text", "SMS_MODAL")
            logger.info("find SMS_TEXT")
            smsText = self.find("text", "SMS_TEXT")
            logger.info(smsText)
            logger.info("find SMS_SUBMIT")
            smsSubmit = self.find("text", "SMS_SUBMIT")
            logger.info(smsSubmit)

            text_sms = input("Please Enter SMS code in 60 seconds: ")
            smsText.clear()
            logger.info("send_keys smsText")
            smsText.send_keys(text_sms)
            logger.info(smsText)
            smsSubmit.click()
            try:
                self.wait_until("css", "AVATAR")
            except:
                smsError = self.find("css", "LOGIN_FAILED")
                if len(smsError) > 0:
                    logger.error("Sending SMS code "+smsError[0].text)
                else:
                    logger.error("Sending SMS code Run time out.")
                self.close()
                sys.exit(0)
        except Exception as e:
            logger.info("No need SMS authenticate"+repr(e))

    def clickCoin(self):
        try:
            self.getRequest("COIN_PAGE")
            logger.debug("wait_until COIN_PAGE_READY")
            self.wait_until("text", "COIN_PAGE_READY")
            try:
                logger.debug("wait_until GET_COIN")
                self.wait_until("text", "GET_COIN")
                logger.debug("find COIN_NOW")
                current_coin = self.find("text", "COIN_NOW")
                logger.debug(current_coin)
                logger.debug("find get_coin")
                get_coin = self.find("text", "GET_COIN")
                logger.debug(get_coin)

                logger.info("目前有：" + current_coin.text +
                            " 蝦幣，" + get_coin.text)

                logger.debug("click get_coin")
                get_coin.click()
            except Exception as e:
                logger.error(str(e))
                logger.info("今天已經獲取過蝦幣")

            logger.debug("wait_until COIN_REGULAR")
            self.wait_until("text", "COIN_REGULAR")
            current_coin = self.find("text", "COIN_NOW")
            logger.debug("find COIN_REGULAR")
            coin_regular = self.find("text", "COIN_REGULAR")
            logger.info("目前有：" + current_coin.text +
                        " 蝦幣，" + coin_regular.text)
        except Exception as e:
            logger.error(repr(e))
            self.close()

    def run(self):
        self.getRequest("INDEX")
        self.checkPopModal()
        self.loginByCookie(cookie_name)
        if not self.checkLogin():
            self.loginByPass()
            if not self.checkLogin():
                sleep(3)
                self.checkSMS()
                if not self.checkLogin():
                    self.close()
        self.saveCookie(cookie_name)
        self.clickCoin()
        self.close()

    def close(self):
        self.driver.close()
        logger.info("Program exit")
        sys.exit(0)


if __name__ == "__main__":
    Crawler().run()
