from urllib.parse import urlparse, parse_qs
from hashlib import *

import copy
import os
import time
import random
import requests as fw
import uuid
import json
import segno

def ds1(salt):
    t = int(time.time())
    a = random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",6)
    r = ''.join(random.choices(a,k=6))
    main = f"salt={salt}&t={t}&r={r}"
    d = md5(main.encode(encoding='UTF-8')).hexdigest()
    return f'{t},{r},{d}'

def ds2(salt,b='',q=''):
    body = json.dumps(obj=b, sort_keys=True)
    query = "&".join(sorted(f"{q}".split("&")))
    t = int(time.time())
    r = random.randint(100000, 200000)
    if r == 100000:
        r = 642367
    main = f"salt={salt}&t={t}&r={r}&b={body}&q={query}"
    ds = md5(main.encode(encoding='UTF-8')).hexdigest()
    return f"{t},{r},{ds}"

GET_FP_URL = 'https://public-data-api.mihoyo.com/device-fp/api/getFp'

mysVersion = '2.51.1'
_HEADER = {
    'x-rpc-app_version': mysVersion,
    'User-Agent': (
        'Mozilla/5.0 (Linux; Android 13; M2101K9C Build/TKQ1.220829.002; wv) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.76 '
        f'Mobile Safari/537.36 miHoYoBBS/{mysVersion}'
    ),
    'x-rpc-client_type': '5',
    'Referer': 'https://webstatic.mihoyo.com/',
    'Origin': 'https://webstatic.mihoyo.com',
}

def generate_seed(length: int):
    characters = '0123456789abcdef'
    result = ''.join(random.choices(characters, k=length))
    return result

device = uuid.uuid4()

def generate_fp_by_uid():
    seed_id = generate_seed(16)
    seed_time = str(int(time.time() * 1000))
    ext_fields = f'{{"userAgent":"{_HEADER["User-Agent"]}",\
    "browserScreenSize":281520,"maxTouchPoints":5,\
    "isTouchSupported":true,"browserLanguage":"zh-CN","browserPlat":"iPhone",\
    "browserTimeZone":"Asia/Shanghai","webGlRender":"Apple GPU",\
    "webGlVendor":"Apple Inc.",\
    "numOfPlugins":0,"listOfPlugins":"unknown","screenRatio":3,"deviceMemory":"unknown",\
    "hardwareConcurrency":"4","cpuClass":"unknown","ifNotTrack":"unknown","ifAdBlock":0,\
    "hasLiedResolution":1,"hasLiedOs":0,"hasLiedBrowser":0}}'
    body = {
        'seed_id': seed_id,
        'device_id': device.hex,
        'platform': '4',
        'seed_time': seed_time,
        'ext_fields': ext_fields,
        'app_name': 'bbs_cn',   #account_cn
        'device_fp': '38d803971d929',
    }
    HEADER = copy.deepcopy(_HEADER)
    res = fw.post(url=GET_FP_URL,headers=HEADER,json=body)
    res = json.loads(res.text)
    device_fp = res['data']['device_fp']
    return device_fp

def get_headers(url,x_rpc_client_type,ds,cookies):
    o1 = f'{url}'
    o1 = o1.split('/', 3)
    Origin = f'{o1[0]}//{o1[2]}'
    h = {"Accept-Language": "zh-cn,zh;q=0.5", "Accept-Charset": "UTF-8", "Origin": f"{Origin}",
         "X-Requested-With": "com.mihoyo.hyperion", "x-rpc-device_id": f"{device}",
         'x-rpc-device_fp': f'{generate_fp_by_uid()}', "x-rpc-app_version": f"{mysVersion}",
         "User-Agent": f"{_HEADER["User-Agent"]}",
         "Referer": "", "x-rpc-client_type": f"{x_rpc_client_type}", "x-rpc-page": "",
         "DS": f"{ds}", "Cookie": f"{cookies}", "Host": f"{o1[2]}"}
    if x_rpc_client_type == 5:
        h['Referer'] = 'https://webstatic.mihoyo.com'
    elif x_rpc_client_type == 4:
        h['Referer'] = 'https://www.miyoushe.com'
    elif x_rpc_client_type == 2:
        h['Referer'] = 'https://app.mihoyo.com'
    return h

class mys_api:

    def __init__(self):
        self.data = {}
        self.uid = 0

    def GET_Qr_login(self):
        h = {'x-rpc-app_id':'bll8iq97cem8','x-rpc-device_id':f'{device}'}
        a = fw.post(url='https://passport-api.miyoushe.com/account/ma-cn-passport/web/createQRLogin',headers=h)
        #b = a.headers
        a = json.loads(a.text)
        url = a['data']['url']
        # 生成二维码
        qr = segno.make_qr(url)
        qr.save('img.png', scale=10)
        if a['retcode'] != 0:
            print(a)
        else:
            url1 = urlparse(url)
            url2 = parse_qs(url1.query)
            ticket = url2.get('tk')[0]
            self.data = {}
            self.data['qr_code'] = f'{os.getcwd()}/img.png'
            self.data['tk'] = ticket
            return self.data

    def GET_Qr_login_1(self,ticket):
        while True:
            h = {'x-rpc-app_id': 'bll8iq97cem8', 'x-rpc-device_id': f'{device}'}
            body = {'ticket':f'{ticket}'}
            a = fw.post(url='https://passport-api.miyoushe.com/account/ma-cn-passport/web/queryQRLoginStatus', headers=h, json=body)
            b = a.headers
            c = a.cookies
            a = json.loads(a.text)
            if a['retcode'] != 0:
                self.data['login'] = a
                return self.data
            elif a['data']['status'] != 'Confirmed':
                pass
                continue
            else:
                z = {}
                for d in c:
                    z[d.name] = d.value
                    with open(f'{os.getcwd()}/Token.json','w',encoding='utf-8') as f:
                        json.dump(z,f)
                self.data = {}
                self.data['login'] = '登陆成功'
                return self.data

    def Hk4eToken(self,uid):
        cookies = self.cookie()
        h = {'Cookie':f'{cookies}'}
        body = {"region":"cn_gf01","uid":f"{uid}","game_biz":"hk4e_cn"}
        a = fw.post('https://api-takumi.mihoyo.com/common/badge/v1/login/account',headers=h,json=body)
        a = json.loads(a.text)
        if a['retcode'] == 0:
            with open('yuan_shen_Hk4eToken.json', 'w', encoding='utf-8') as f:
                json.dump(a['data'],f)
                self.data = {}
                self.data['play'] = '获取基础信息成功，尝试获取登陆信息'
                self.uid = uid
            return self.data
        else:
            self.data = {}
            self.data['play'] = f'获取基础信息失败，错误返回{a}'
            return self.data


    def cookie(self,token=''):
        if token == '':
            with open('Token.json', 'r', encoding='utf-8') as f:
                cookie_1 = json.load(f)
                cookie = ''
                for key, value in cookie_1.items():
                    cookie += f'{key}={value};'
                cookie += f'DEVICEFP_SEED_TIME={int(time.time() * 1000)}'
            return cookie
        else:
            with open('Token.json', 'r', encoding='utf-8') as f:
                cookie = json.load(f)
                return cookie[token]

    def yuan_shen_jue_se_data(self):
        cookies = self.cookie()
        body = ''
        q = f'role_id={self.uid}&server=cn_gf01'
        salt = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
        h = get_headers(url='https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index',
                        x_rpc_client_type='5', ds=f'{ds2(salt, body, q)}', cookies=f'{cookies}')
        h['x-rpc-device_id'] = '393b7391-3cf6-498c-8f7e-197fda0496a0'
        h['x-rpc-device_fp'] = '38d803971d929'
        a = fw.get(
            f'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index?server=cn_gf01&role_id={self.uid}',
            headers=h)
        a = json.loads(a.text)
        if a['retcode'] == 0:
            with open('yuan_shen_jue_se_data.json', 'w', encoding='utf-8') as f:
                json.dump(a['data'], f)
            return '获取角色信息成功'
        else:
            return f'获取角色信息失败，错误返回{a}'


mys_api = mys_api()
