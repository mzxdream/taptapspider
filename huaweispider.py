#!/usr/bin/env python3

from selenium import webdriver
from datetime import datetime
import time
import re
import os

options = webdriver.ChromeOptions()
# 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
options.add_experimental_option('excludeSwitches', ['enable-automation']) 
browser = webdriver.Chrome(executable_path="/bin/chromedriver", options=options)

#timeout
browser.set_page_load_timeout(3)

try:
    browser.get("https://www.vmall.com")
except:
    pass
time.sleep(60)

endTime = datetime.strptime("2020-3-11 10:08:00", "%Y-%m-%d %H:%M:%S")

while True:
    try:
        try:
            browser.get("https://www.vmall.com/product/10086108539274.html")
        except:
            pass
        item = browser.find_elements_by_css_selector('.product-button a')
        if len(item) > 0:
            item = item[0]
            print(item.get_attribute("class"))
            if item.get_attribute("class").find("disabled") == -1:
                item.click()
                break
    except:
        pass
    nowTime = datetime.now()
    delta = (endTime - nowTime).total_seconds()
    print("当前时间:", nowTime, " 倒计时:", delta)
    if delta > 60:
        time.sleep(40)
    elif delta > 10:
        time.sleep(5)
    elif delta > 3:
        time.sleep(1)
