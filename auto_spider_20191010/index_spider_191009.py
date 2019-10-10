import requests
import random
import json
import os
from tqdm import tqdm


PROXY = None
_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',}
_SESSION = requests.session()
HOST = 'https://club.autohome.com.cn/'
BBS_DICT = {'mingrui': 519, 'kediyake': 4217}


def get_request(url, param=None):
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
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


def get_a_page(bbs_name, page_index=1):
    url = 'https://club.autohome.com.cn/frontapi/topics/getByBbsId'
    params = {'pageindex': page_index,
              'pagesize': 100,
              'bbs': 'c',
              'bbsid': BBS_DICT[bbs_name],
              'fields': 'topicid,title,post_memberid,post_membername,postdate,ispoll,ispic,isrefine,'
                        'replycount,viewcount,videoid,isvideo,videoinfo,qainfo,tags,topictype,imgs,'
                        'jximgs,url,piccount,isjingxuan,issolve,liveid,livecover,topicimgs',
              'orderby': 'lastpostdata-'
              }

    resp_text = get_request(url, params)
    dir_path = os.path.join(os.getcwd(), 'result', 'index', bbs_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, '%d.json' % page_index)
    with open(file_path, 'w') as fw:
        fw.write(resp_text)
    result_dict = json.loads(resp_text)
    count = result_dict['result']['pagecount']
    # print('%s: page %d is done!' % (bbs_name, page_index))
    return count


def run(bbs_name):
    page_count = get_a_page(bbs_name)
    print('%s has %d pages' % (bbs_name, page_count))
    for i in tqdm(range(2, page_count+1)):
        get_a_page(bbs_name, i)


if __name__ == '__main__':
    for k in BBS_DICT.keys():
        run(k)
