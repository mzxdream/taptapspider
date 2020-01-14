#!/usr/bin/env python3

from selenium import webdriver
import time
import re
import os
import threading
import _thread

def ReadTalkDetail():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    browser = webdriver.Chrome(executable_path="/bin/chromedriver", options=options)
    browser.get('https://www.taptap.com/app/137515/review?order=update&page=1#review-list')
    f = open("user.csv", "w")
    while True:
        time.sleep(3)
        try:
            items = browser.find_elements_by_css_selector('.review-item-text')
            for item in items:
                name = ""
                try:
                    name = item.find_element_by_css_selector('.review-item-text > div.item-text-header a.taptap-user-name').text
                except:
                    print("get name failed")
                    continue

                gametime = ""
                try:
                    gametime = item.find_element_by_css_selector('span.text-score-time').text
                except:
                    pass
                gametimestr = re.findall(r"\d+\.?\d*", gametime)
                gametime = 0
                if len(gametimestr) >= 1:
                    gametime = int(gametimestr[-1])
                    if len(gametimestr) >= 2:
                        gametime = gametime + int(gametimestr[-2]) * 60
                gametime = str(gametime)

                star = ""
                try:
                    star = item.find_element_by_css_selector('.review-item-text > div.item-text-score i.colored').get_attribute('style')
                except:
                    print("get star failed")
                    continue
                starstr = re.findall(r"\d+", star)
                star = 1
                if len(starstr) >= 1:
                    star = int(starstr[-1]) / 14
                star = str(star)

                content = ""
                try:
                    content = item.find_element_by_css_selector('.review-item-text > div.item-text-body').text
                except:
                    print("get content failed")
                    continue
                outstr = '"' + name + '","' + gametime  + '","' + star + '","' + content + '",\n'
                print(outstr)
                f.write(outstr)
        except Exception as e:
            print("find items failed:", e)
        try:
            nextUrls = browser.find_elements_by_css_selector('.taptap-button-more a')
            nextUrl = ""
            for url in nextUrls:
                if url.text == ">":
                    nextUrl = url.get_attribute('href')
                    break
            if nextUrl == "":
                break
            browser.get(nextUrl)
            print(nextUrl)
        except:
            print("get next url failed")
            break
    f.close()

if __name__ == "__main__":
    ReadTalkDetail()
