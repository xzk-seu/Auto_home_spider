import json
import os
import math
from get_index import _get_request
from bs4 import BeautifulSoup
from multiprocessing import Pool


HOST = 'https://club.autohome.com.cn/'


# 根据回复数获取一个帖子的页数
def get_page_count(reply_count):
    # 每页显示20个回复，0回复也有一页
    page = math.ceil(reply_count / 20)
    if page == 0:
        page = 1
    return page


# 获取一个帖子单页的内容
def get_page_content(url):
    result_list = list()
    r = _get_request(url)
    soup = BeautifulSoup(r, 'lxml')
    conright_list = soup.find_all('div', 'conright fr')
    for c in conright_list:
        s = c.text.strip()
        result_list.append(s.strip())
    conright_list = soup.find_all('div', 'conright fl')
    for c in conright_list:
        s = c.text.strip()
        result_list.append(s.strip())
    return result_list


# 获得一个帖子的所有页的内容
def get_content(index):
    reply_count = int(index['reply_count'])
    page_count = get_page_count(reply_count)
    href = index['href']
    href_template = href.replace('-1.html', '-%d.html')
    print(href_template)
    for page in range(1, page_count+1):
        url = HOST+(href_template % page)
        print(url)
        page_content = get_page_content(url)
        print(page_content)
        break
    return 1


# 主程序入口
def run():
    path = os.path.join(os.getcwd(), 'index', 'rongwei', '1.json')
    with open(path, 'r') as fr:
        index_list = json.load(fr)
    for index in index_list:
        print(index)
        content = get_content(index)
        break


if __name__ == '__main__':
    run()
    # 爬取第几页的第几个帖子的第几页
