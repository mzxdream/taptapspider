#!/usr/bin/env python3

from selenium import webdriver
import time
import re
import os
import threading
import _thread

class GameInfo:
    def __init__(self, name, gametime, score, title):
        self.name = name
        self.score = score
        self.title = title
        self.hour = 0
        self.minute = 0
        gametimes = re.findall(r"\d+\.?\d*", gametime)
        if len(gametimes) >= 2:
            self.hour = int(gametimes[0])
        if len(gametimes) >= 1:
            self.minute = int(gametimes[-1])
        self.gametime = self.hour * 60 + self.minute

class UserInfo:
    def __init__(self, name, gametime, url):
        self.name = name 
        self.url = url
        self.games = {}
        self.hour = 0
        self.minute = 0
        gametimes = re.findall(r"\d+\.?\d*", gametime)
        if len(gametimes) >= 2:
            self.hour = int(gametimes[0])
        if len(gametimes) >= 1:
            self.minute = int(gametimes[-1])
        self.gametime = self.hour * 60 + self.minute

#init users
users = {}

if os.path.exists("user.csv"):
    with open("user.csv") as f:
        for line in f:
            datas = line.split(",")
            if len(datas) < 4:
                continue
            name = datas[0]
            gametime = datas[1] + ":" + datas[2]
            url = datas[3]
            users[name] = UserInfo(name, gametime, url)
else:
    options = webdriver.ChromeOptions()
    # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    options.add_experimental_option('excludeSwitches', ['enable-automation']) 
    browser = webdriver.Chrome(executable_path="/bin/chromedriver", options=options)
    browser.get('https://www.taptap.com/app/7133/review?order=update#review-list')
    while True:
        time.sleep(3)
        try:
            items = browser.find_elements_by_css_selector('li.taptap-review-item')
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
                url = ""
                try:
                    url = item.find_element_by_css_selector('a').get_attribute('href')
                except:
                    print("get url failed")
                users[name] = UserInfo(name, gametime, url)
        except:
            print("find items failed")
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
        except:
            print("get next url failed")
            break
    f = open("user.csv", "w")
    for name in users:
        user = users[name]
        f.write(user.name + "," + str(user.hour) + "," + str(user.minute) + "," + user.url + ", \n")
    f.close()

#遍历用户
f = open("detail.csv", "r+")
for line in f:
    datas = line.split(",")
    if len(datas) < 1:
        continue
    name = datas[0]
    print("1111:" + name)
    users.pop(name, None)
    print(name + " has read")

users = list(users.values())
#spider
lock = threading.Lock()
nextIndex = 0
def Spider():
    global nextIndex
    options = webdriver.ChromeOptions()
    # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    options.add_experimental_option('excludeSwitches', ['enable-automation']) 
    #options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    browser = webdriver.Chrome(executable_path="/bin/chromedriver", options=options)
    browser.get('https://www.taptap.com/auth/login')
    time.sleep(60)
    
    index = 0
    lock.acquire()
    index = nextIndex
    nextIndex += 1
    lock.release()
    
    while index < len(users):
        user = users[index]
        print("index:", str(index), " user:", user.name, ",", user.gametime, ",", user.url)

        lock.acquire()
        index = nextIndex
        nextIndex += 1
        lock.release()

        if user.url == "":
            continue
        try:
            browser.get(user.url)
        except:
            print("to user url failed:", user.name, ",", user.gametime, ",", user.url)
            continue
        while True:
            try:
                time.sleep(3)
                items = browser.find_elements_by_css_selector('.active div.app-item-detail')
                for item in items:
                    name = ""
                    gametime = ""
                    score = ""
                    title = ""
                    try:
                        name = item.find_element_by_css_selector('.app-item-title a').text
                    except:
                        print("get game name failed")
                        continue
                    try:
                        gametime = item.find_element_by_css_selector('span.play_time').text
                    except:
                        #print("get game time failed")
                        pass
                    try:
                        score = item.find_element_by_css_selector('span.app-score').text
                    except:
                        print("get game score failed")
                    try:
                        title = item.find_element_by_css_selector('p').text
                    except:
                        print("get game title failed")
                    #print("xxxxxxxxxxxxx:", name, " ", gametime, " ", score, " ", title)
                    user.games[name] = GameInfo(name, gametime, score, title)
            except:
                print("get user games failed:", user.name)
            try:
                nextUrls = browser.find_elements_by_css_selector('.pagination a')
                nextUrl = ""
                for url in nextUrls:
                    if url.text == ">":
                        nextUrl = url.get_attribute('href')
                        break
                if nextUrl == "":
                    break
                browser.get(nextUrl)
            except:
                print("get next url failed")
                break
        lock.acquire()
        f.write(user.name + "," + str(user.hour) + "," + str(user.minute) + ",")
        i = 0
        for game in sorted(user.games.values(), key=lambda g: g.gametime, reverse=True):
            if i >= 10:
                break
            f.write(game.name + "," + str(game.hour) + "," + str(game.minute) + "," + game.score + "," + game.title + ",")
            i += 1
        f.write("\n")
        f.flush()
        lock.release()
while True:
    cmd = input("press a to add new thread")
    if cmd == "exit":
        break
    if cmd == "a": 
        _thread.start_new_thread(Spider, ())

f.close()
