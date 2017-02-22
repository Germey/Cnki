from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import sample
import pytesseract
import requests
from PIL import Image
from io import BytesIO
from hashlib import md5

driver = webdriver.PhantomJS()

def get_code(url, items):
    cookies = {}
    for item in items:
        cookies[item['name']] = item['value']
    content = requests.get(url, cookies=cookies).content
    image = Image.open(BytesIO(content))
    try:
        code = pytesseract.image_to_string(image)
    except UnicodeDecodeError:
        return ''
    return code


def get_page():
    try:
        driver.get('http://my.cnki.net/elibregister/commonRegister.aspx')
        checkcode = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "checkcode"))
        )
        src = checkcode.get_attribute('src')
        code = get_code(src, driver.get_cookies())
        print('识别结果:', code)
        input_username = driver.find_element_by_id('txtUserName')
        input_password = driver.find_element_by_id('txtPassword')
        input_confirm = driver.find_element_by_id('ConfirmPass')
        input_email = driver.find_element_by_id('txtEmail')
        input_code = driver.find_element_by_id('txtOldCheckCode')
        input_button = driver.find_element_by_id('LinkButton1')
        random_string = ''.join(sample('zyxwvutsrqponmlkjihgfedcba', 10))
        input_username.send_keys(random_string)
        password = md5(random_string.encode('utf-8')).hexdigest()
        input_password.send_keys(password)
        input_confirm.send_keys(password)
        random_email = random_string + '@' + random_string + '.com'
        input_email.send_keys(random_email)
        input_code.send_keys(code)
        input_button.click()
        result = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.main h2 img'))
        )
        if result: print('注册成功，用户名', random_string, '密码', password, '邮箱', random_email)

    except UnexpectedAlertPresentException as e:
        Alert(driver).accept()
        print(e.msg)
        get_page()
    except TimeoutException as e:
        print('请求超时', e.msg)
        get_page()
    finally:
        driver.quit()
        pass


get_page()
