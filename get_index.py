# 获取一个目录页面下所有帖子的地址
import json
import os
import requests
import random
from bs4 import BeautifulSoup
from multiprocessing import Pool


PROXY = {'http': 'http://DONGNANHTT1:T74B13bQ@http-proxy-sg2.dobel.cn:9180',
         'https': 'http://DONGNANHTT1:T74B13bQ@http-proxy-sg2.dobel.cn:9180'}
_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',}
_SESSION = requests.session()
HOST = 'https://club.autohome.com.cn/'


def _get_request(url, param=None):
    resp = _SESSION.get(
        url,
        params=param,
        headers=_HEADERS,
        proxies=PROXY,
        timeout=random.choice(range(30, 100))
    )
    resp.encoding = resp.apparent_encoding
    # "utf-8"
    if resp.status_code == 200:
        return resp.text
    elif resp.status_code == 404:
        return ''
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
        print('in safe_wire: %s' % e)


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

    c_type = 'xinsiyu'
    v = config[c_type]
    run(v['page_limit'], c_type, v['id'])

