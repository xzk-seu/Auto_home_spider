import json
import os
from multiprocessing import Pool
from get_index import get_index


def write_result(page):
    path = os.path.join(os.getcwd(), 'index', 'boyue')
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, str(page)+'.json')
    if os.path.exists(file_path) and os.path.getsize(file_path) != 0:
        print('file: %d is existing!' % page)
        return

    url = 'https://club.autohome.com.cn/bbs/forum-c-3788-%d.html'
    temp = get_index(url % page)
    with open(file_path, 'w') as fw:
        json.dump(temp, fw)
        print('PAGE: %d done!' % page)


def safe_write(page):
    try:
        write_result(page)
    except Exception as e:
        print('in safe_wire: %s' % e)


def get_boyue_index(page_limit):
    pool = Pool(8)
    for i in range(1, page_limit + 1):
        pool.apply_async(safe_write, args=(i,))
    pool.close()
    pool.join()


if __name__ == '__main__':
    get_boyue_index(1000)

