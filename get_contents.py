import json
import os
import math
from get_index import _get_request
from bs4 import BeautifulSoup
from multiprocessing import Pool
import shutil


HOST = 'https://club.autohome.com.cn/'


# 根据回复数获取一个帖子的页数
def get_page_count(reply_count):
    # 每页显示20个回复，0回复也有一页
    page = math.ceil(reply_count / 20)
    if page == 0:
        page = 1
    return page


# 从页面中解析出楼主发帖
def get_top_floor(soup):
    r_dict = dict()
    f0 = soup.find('div', id='F0')
    if not f0:
        print('此地址也许是视频， pass。。。')
        return None
    temp = f0.find('div', 'conright fr')
    info_0 = temp.contents[1]
    floor = info_0.contents[1].string
    time = info_0.contents[6].string
    info_1 = temp.contents[3]
    content = info_1.contents[5].text

    r_dict['floor'] = floor
    r_dict['time'] = time
    r_dict['content'] = content
    return r_dict


# 获取某一楼的回复
def get_reply_floor(soup, floor_num):
    r_dict = dict()
    raw_floor = soup.find('div', id='F%d' % floor_num)
    if not raw_floor:
        return None

    raw_floor = raw_floor.contents[5]
    raw_floor = raw_floor.contents[1]
    info = raw_floor.contents[1]
    floor = info.contents[1].text
    time = info.find('span', xname="date").text
    content = raw_floor.contents[3].text

    r_dict['floor'] = floor
    r_dict['time'] = time
    r_dict['content'] = content
    return r_dict
    # for n, j in enumerate(raw_floor.contents):
    #     print(n, j)


# 获取一个帖子单页的内容
# 第index_num个帖子的第page页
# 根据当前页码和回复数量知道要获得的帖子是几楼到几楼
def get_page_content(url, page, reply_count, index_num):
    path = os.path.join(os.getcwd(), 'temp')
    if not os.path.exists(path):
        os.makedirs(path)
    f_path = os.path.join(path, 'temp_%d_%d.json' % (index_num, page))
    if os.path.exists(f_path) and os.path.getsize(f_path) != 0:
        print('temp_%d_%d.json is EXISTED!' % (index_num, page))
        return

    result_list = list()
    r = _get_request(url)
    soup = BeautifulSoup(r, 'lxml')

    if page == 1:
        top_floor = get_top_floor(soup)
        if not top_floor:
            with open(f_path, 'w') as fw:
                json.dump(result_list, fw)
                print('TEMP FILE: temp_%d_%d.json is done!' % (index_num, page))
                return
        result_list.append(top_floor)

    # begin = (page-1) * 20 + 1
    end = page * 20
    begin = end - 19
    if end > reply_count:
        end = reply_count
    for i in range(begin, end):
        reply = get_reply_floor(soup, i)
        if not reply:
            with open(f_path, 'w') as fw:
                json.dump(result_list, fw)
                print('TEMP FILE: temp_%d_%d.json is done!' % (index_num, page))
                return
        result_list.append(reply)

    with open(f_path, 'w') as fw:
        json.dump(result_list, fw)
        print('TEMP FILE: temp_%d_%d.json is done!' % (index_num, page))
    # return result_list


def safe_get_page_content(url, page, reply_count, index_num):
    try:
        get_page_content(url, page, reply_count, index_num)
    except Exception as e:
        print('IN safe_get_page_content: %s' % e)
        print('url: ', url)
        print('page: ', page)
        print('reply_count: ', reply_count)
        print('index_num: ', index_num)
        print('----------------------------------')


# 获得一个帖子的所有页的内容
def get_content(index, index_num, pool):
    reply_count = int(index['reply_count'])
    page_count = get_page_count(reply_count)
    href = index['href']
    href_template = href.replace('-1.html', '-%d.html')
    for page in range(1, page_count+1):
        url = HOST+(href_template % page)
        pool.apply_async(safe_get_page_content, args=(url, page, reply_count, index_num))
        # page_content = get_page_content(url, page, reply_count, index_num)
        # # print(page_content)
    # return 1


# 计算并发获得的临时文件应有数量
# 与已有数量进行比较返回布尔值
def temp_check(index_path):
    temp_path = os.path.join(os.getcwd(), 'temp')
    temp_list = os.listdir(temp_path)
    existing = len(temp_list)

    should = 0
    with open(index_path, 'r') as fr:
        index_list = json.load(fr)
    for index in index_list:
        reply_count = int(index['reply_count'])
        should += get_page_count(reply_count)

    if existing == should:
        print('get all temp for %s' % index_path)
        return True
    else:
        return False


# 将并发获得的临时文件合并
def temp_merge(index_path, index_page_num, car_type):
    r_list = list()
    with open(index_path, 'r') as fr:
        index_list = json.load(fr)
    for n, index in enumerate(index_list):
        content_list = list()
        reply_count = int(index['reply_count'])
        page_count = get_page_count(reply_count)
        for p in range(1, page_count+1):
            temp_path = os.path.join(os.getcwd(), 'temp', 'temp_%d_%d.json' % (n, p))
            with open(temp_path, 'r') as fr:
                temp = json.load(fr)
            content_list.extend(temp)
        index['content'] = content_list
        r_list.append(index)

    r_path = os.path.join(os.getcwd(), 'result', car_type)
    if not os.path.exists(r_path):
        os.makedirs(r_path)
    path = os.path.join(r_path, '%d.json' % index_page_num)
    with open(path, 'w') as fw:
        json.dump(r_list, fw)
        print('%s is done!!!' % path)
    temp_path = os.path.join(os.getcwd(), 'temp')
    shutil.rmtree(temp_path)
    os.makedirs(temp_path)


# 从特定车型、页码的索引文件中读出帖子的地址，计算帖子一共有多少页，然后进行并行爬取
# 获得的结果存在temp文件夹中
# 全部获取到之后，合并temp文件夹中的文件，删除temp文件夹
def process_from_index(index_page_num, car_type):
    r_path = os.path.join(os.getcwd(), 'result', car_type)
    if not os.path.exists(r_path):
        os.makedirs(r_path)
    path = os.path.join(r_path, '%d.json' % index_page_num)
    if os.path.exists(path):
        print('%s is EXISTED!!!!' % path)
        return

    index_path = os.path.join(os.getcwd(), 'index', car_type, '%d.json' % index_page_num)
    while True:
        pool = Pool(8)
        with open(index_path, 'r') as fr:
            index_list = json.load(fr)
        for n, index in enumerate(index_list):
            get_content(index, n, pool)
        pool.close()
        pool.join()
        if temp_check(index_path):
            break
    temp_merge(index_path, index_page_num, car_type)


# 主程序入口
def run():
    car_type = 'rongwei'
    page_limit = 1000

    # for index_page_num in range(1, page_limit+1):
    #     process_from_index(index_page_num, car_type)
    for index_page_num in range(1, page_limit+1):
        process_from_index(index_page_num, car_type)
    # index_page_num = 1
    # process_from_index(index_page_num, car_type)


if __name__ == '__main__':
    run()
