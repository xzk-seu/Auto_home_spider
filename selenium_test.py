import json
import os
import requests
import random
from selenium import webdriver


_SESSION = requests.session()
PROXY = {'http': 'http://DONGNANHTT1:T74B13bQ@http-proxy-t1.dobel.cn:9180',
         'https': 'http://DONGNANHTT1:T74B13bQ@http-proxy-t1.dobel.cn:9180'}
_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
HOST = 'https://club.autohome.com.cn/'


def _get_selenium_cookie(url):
    chrome_driver = 'C:\Program Files\chromedriver_win32\chromedriver.exe'
    browser = webdriver.Chrome(executable_path=chrome_driver)
    browser.get(url)
    # print(browser.page_source)
    cookie = browser.get_cookies()
    browser.close()
    return cookie


def run():
    count = 0
    while True:
        url = 'https://club.autohome.com.cn//bbs/thread/372b743cbd013cf1/75477343-6.html'
        chrome_driver = 'C:\Program Files\chromedriver_win32\chromedriver.exe'
        browser = webdriver.Chrome(executable_path=chrome_driver)
        browser.get(url)
        cookie = browser.get_cookies()
        # with open('cookie_%d.json' % count, 'w') as fw:
        #     json.dump(cookie, fw)
        count += 1
        print(cookie)
        text = browser.page_source
        error_text = ['您访问的页面出错了！', '请先拖动验证码到相应位置']
        for t in error_text:
            if t in text:
                print(url, t)
                return
        browser.close()


def cookie_process():
    c_dict = dict()
    for i in range(4):
        with open('cookie_%d.json' % i, 'r') as fr:
            temp = json.load(fr)
        for d in temp:
            if d['name'] not in c_dict.keys():
                t = list()
                t.append(i)
                c_dict[d['name']] = t
            else:
                c_dict[d['name']].append(i)
    print(c_dict)


def _get_request(url, param=None, cookie=None):
    print(cookie)
    resp = _SESSION.get(
        url,
        params=param,
        headers=_HEADERS,
        # proxies=PROXY,
        cookies=cookie,
        timeout=random.choice(range(30, 100))
    )
    resp.encoding = resp.apparent_encoding
    cookie = resp.cookies.get_dict()
    print('new', cookie)
    # "utf-8"
    if resp.status_code == 200:
        return resp.text
    elif resp.status_code == 404:
        return ''
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


def get_cookie(i):
    cookie = dict()
    with open('cookie_%d.json' % i, 'r') as fr:
        temp = json.load(fr)
    for d in temp:
        cookie[d['name']] = d['value']
    return cookie


if __name__ == '__main__':
    # run()
    # cookie_process()
    url = 'https://club.autohome.com.cn//bbs/thread/372b743cbd013cf1/75477343-6.html'
    c1 = {'autotc': '2C21CFC7F740EC60B261233634D43881'}
    c2 = {'autotc': '850E00fb55983f61'}
    c3 = {'autotc': '9F0FDF080C544CBD1532DCB7E6D4680F'}
    c = [c1, c2, c3]
    i = 0
    while True:
        r = _get_request(url, None, c[i])
        # error_text = ['您访问的页面出错了！', '请先拖动验证码到相应位置']
        if '请先拖动验证码到相应位置' in r:
            print(url, '请先拖动验证码到相应位置')
            i = (i+1) % 3
            # print(r)
