import requests
import random
import json


PROXY = None
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
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


def run():
    url = 'https://club.autohome.com.cn/frontapi/topics/getByBbsId'
    params = {'pageindex': 1,
              'pagesize': 50,
              'bbs': 'c',
              'bbsid': 519,
              'fields': 'topicid,title,post_memberid,post_membername,postdate,ispoll,ispic,isrefine,'
                        'replycount,viewcount,videoid,isvideo,videoinfo,qainfo,tags,topictype,imgs,'
                        'jximgs,url,piccount,isjingxuan,issolve,liveid,livecover,topicimgs',
              'orderby': 'lastpostdata-'
              }

    resp_text = _get_request(url, params)
    with open('test.json', 'w') as fw:
        fw.write(resp_text)
    result_dict = json.loads(resp_text)
    count = result_dict['result']['pagecount']
    print(count)


if __name__ == '__main__':
    run()
