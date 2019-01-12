# 获取一个目录页面下所有帖子的地址
import json
import os
import requests
import random
from bs4 import BeautifulSoup
from multiprocessing import Pool
from selenium import webdriver

# PROXY = {'http': 'http://DONGNANHTT1:T74B13bQ@http-proxy-sg2.dobel.cn:9180',
#          'https': 'http://DONGNANHTT1:T74B13bQ@http-proxy-sg2.dobel.cn:9180'}

PROXY = {'http': 'http://DONGNANHTT1:T74B13bQ@http-proxy-t1.dobel.cn:9180',
         'https': 'http://DONGNANHTT1:T74B13bQ@http-proxy-t1.dobel.cn:9180'}

# _HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
#             'Host': 'https://club.autohome.com.cn/',
#             'Connection': 'keep-alive',
#             'Cache-Control': 'max-age=0',
#             'Upgrade-Insecure-Requests': '1',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Accept-Language': 'zh-CN,zh;q=0.9'}
            # 'Cookie': '__ah_uuid=9950D635-C8B9-48D7-9AA3-6F07F8F225F2; fvlid=15447539049017Z9cwlUan8; sessionid=60E922E8-629D-4327-8411-C3A70D7473E3%7C%7C2018-12-14+10%3A18%3A35.541%7C%7C0; area=320115; ahpau=1; sessionip=58.213.113.80; sessionvid=D953A650-600E-4C38-9107-18E4015A6330; papopclub=E09C4C265FDC6A11C2475010786C0D4C; pbcpopclub=56ea70ec-046b-4b36-ac53-7bb573cd4834; pepopclub=6C999865FE3D420D4CCA9A8828B570B3; ahpvno=16; ref=0%7C0%7C0%7C0%7C2018-12-20+20%3A28%3A23.284%7C2018-12-14+10%3A18%3A35.541'}
_SESSION = requests.session()
_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
HOST = 'https://club.autohome.com.cn/'
COOKIE = dict()


def _get_request_from_selenium(url):
    chrome_driver = 'C:\Program Files\chromedriver_win32\chromedriver.exe'
    webdriver.Proxy = PROXY
    browser = webdriver.Chrome(executable_path=chrome_driver)
    browser.get(url)
    # print(browser.page_source)
    r = browser.page_source
    browser.close()
    return r


def _get_request(url, param=None):
    # global COOKIE
    # print('set COOKIE', COOKIE)
    resp = _SESSION.get(
        url,
        params=param,
        headers=_HEADERS,
        proxies=PROXY,
        # cookies=COOKIE,
        timeout=random.choice(range(30, 100))
    )
    resp.encoding = resp.apparent_encoding
    # "utf-8"
    if resp.status_code == 200:
        c = resp.cookies.get_dict()
        # print('cookie', c)
        if c != {}:
            COOKIE = resp.cookies.get_dict()
        return resp.text
    elif resp.status_code == 404:
        return '404'
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


# 解析一个帖子的标题
def entry_parse(i):
    topic_raw = i.contents[1]
    href = topic_raw.contents[3]['href']
    topic = topic_raw.contents[3].string
    author_time = i.contents[3]
    author_temp = author_time.contents[1]
    author = [author_temp['href'], author_temp.string]
    time = author_time.contents[2].string
    lang = i['lang']
    langs = str(lang).split('|')
    reply_count = langs[3]

    r_dict = {'href': href,
              'topic': topic,
              'author': author,
              'create_at': time,
              'reply_count': reply_count}

    return r_dict


# 获取一个页面下的标题及地址
def get_index(url):
    page_list = list()
    r = _get_request(url)
    soup = BeautifulSoup(r, 'lxml')
    soup = soup.find_all('div', id='subcontent')[0]
    list_dl = soup.find_all('dl', 'list_dl')
    for i in list_dl:
        if len(i['class']) > 1:
            continue
        try:
            t_dict = entry_parse(i)
        except Exception as e:
            print(e)
            continue

        # print('--------------')
        # print(t_dict)
        page_list.append(t_dict)
        # print('--------------')
    return page_list


def write_result(page, car_type, car_id):
    path = os.path.join(os.getcwd(), 'index', car_type)
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, str(page)+'.json')
    if os.path.exists(file_path) and os.path.getsize(file_path) != 0:
        print(car_type, 'file: %d is existing!' % page)
        return

    url = 'https://club.autohome.com.cn/bbs/forum-c-%d-%d.html'
    temp = get_index(url % (car_id, page))
    with open(file_path, 'w') as fw:
        json.dump(temp, fw)
        print(car_type, 'PAGE: %d done!' % page)


def safe_write(page, car_type, car_id):
    try:
        write_result(page, car_type, car_id)
    except Exception as e:
        print('in safe_write: %s' % e)


# 主程序入口
def run(page_limit, car_type, car_id):
    pool = Pool(8)
    for i in range(1, page_limit + 1):
        pool.apply_async(safe_write, args=(i, car_type, car_id))
    pool.close()
    pool.join()


if __name__ == '__main__':
    config = {'rongwei': {'id': 4080, 'page_limit': 1000},#荣威RX5
              'boyue': {'id': 3788, 'page_limit': 1000},  #博越
              # 'rongwei': {'id': 4080, 'page_limit': 1000},#新朗逸
              'xinsiyu': {'id': 135, 'page_limit': 1000},#新思域
              'kewozi': {'id': 4105, 'page_limit': 604},  #科沃兹
              'langyi': {'id': 614, 'page_limit': 1000}}  #朗逸

    # # c_type = input('please input car type: ')
    # for c_type, v in config.items():
    #     run(v['page_limit'], c_type, v['id'])

    c_type = 'langyi'
    v = config[c_type]
    run(v['page_limit'], c_type, v['id'])

