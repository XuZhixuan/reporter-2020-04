import asyncio
import datetime
import functools
import json
import random
import re
import time

import requests
import schedule

from login import http_build_query, login

storage = {}
timestamp = lambda: int(round(time.time() * 1000))


def run():
    # 获取登陆链接
    url = login()

    # 请求登录链接，设置 Cookie 
    session = requests.Session()
    session.get(url)

    # 获取用户信息
    get_user_info(session)

    # 获取早前表单信息
    get_previous_data(session)

    # 获取提交 UUID
    get_form_uuid(session)

    # 获取事务节点 ID
    get_node_id(session)

    # 从本地文件加载表单模板
    load_form_model()

    # 合成表单
    compile_form()

    # 提交表单
    submit_form(session)

    return True

def get_form_uuid(session):
    window_id = random.randint(0, 10000)
    t = random.randint(0, 1000000)

    url = 'http://one2020.xjtu.edu.cn/EIP/cooperative/openCooperative.htm?' + http_build_query({
        'flowId': '4af591a96fcb6ce5016ffa657723057b',
        '_t': t,
        '_winid': window_id
    })

    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)
    storage['uuid'] = re.search(r'var uuid = \'(.*)\';', response.text).group(1)
    print(' ..... done')
    return
    
def get_user_info(session):
    url = 'http://one2020.xjtu.edu.cn/EIP/api/getUserAttribute.htm'
    
    print('[  OK  ]Requesting: ', url, end='')
    response = session.post(url)
    storage['user_info'] = json.loads(response.text)
    print(' ..... done')

    return

def get_previous_data(session):
    base_url = 'http://one2020.xjtu.edu.cn/EIP/queryservice/query.htm'
    queries = [
        {'name': 'college', 'snumber': 'SYMC', 'id_key': 'XH'},
        {'name': 'class', 'snumber': 'XSBJCX', 'id_key': 'studentno'},
        {'name': 'previous', 'snumber': 'GHHXSJBYJ', 'id_key': 'GH'},
    ]

    storage['form_data'] = {}
    for query in queries:
        url = base_url + '?' + http_build_query({
            'snumber': query['snumber'],
            query['id_key']: storage['user_info']['userId'],
            '_': timestamp()
        })

        print('[  OK  ]Requesting: ', url, end='')
        response = session.get(url)
        storage['form_data'][query['name']] = json.loads(response.text)[0]
        print(' ..... done')

    return

def get_node_id(session):
    url = 'http://one2020.xjtu.edu.cn/EIP/flowNode/createNodeIdByNum.htm'

    print('[  OK  ]Requesting: ', url, end='')
    response = session.post(url, {'num': 1})
    storage['node_id'] = json.loads(response.text)[0]
    print(' ..... done')

    return

def load_form_model():

    print('[  OK  ]Loading Model from: ', 'model.json', end='')
    with open('model.json', 'r', encoding='utf-8') as file:
        model = json.load(file)

    storage['form'] = model
    print(' ..... done')

    return

def compile_form():
    data = [
        {'offsets': 'instJson.uniqueIdentify', 'value': storage['uuid']},
        {'offsets': 'formJson.0.XM', 'value': storage['form_data']['previous']['XM']},
        {'offsets': 'formJson.0.XGH', 'value': storage['form_data']['previous']['XGH']},
        {'offsets': 'formJson.0.SJH', 'value': storage['form_data']['previous']['SJH']},
        {'offsets': 'formJson.0.SZSY', 'value': storage['form_data']['previous']['SZSY'] + '@#@' + storage['form_data']['previous']['SZSY']},
        {'offsets': 'formJson.0.BJ', 'value': storage['form_data']['previous']['BJ'] + '@#@' + storage['form_data']['previous']['BJ']},
        {'offsets': 'formJson.0.JGSSQ1', 'value': storage['form_data']['previous']['JGSSQ1'] + '@#@' + storage['form_data']['previous']['JGSSQ1MC']},
        {'offsets': 'formJson.0.JGSSQ2', 'value': storage['form_data']['previous']['JGSSQ2'] + '@#@' + storage['form_data']['previous']['JGSSQ2MC']},
        {'offsets': 'formJson.0.JGSSQ3', 'value': storage['form_data']['previous']['JGSSQ3'] + '@#@' + storage['form_data']['previous']['JGSSQ3MC']},
        {'offsets': 'formJson.0.JTSSQ1', 'value': storage['form_data']['previous']['JTSSQ1'] + '@#@' + storage['form_data']['previous']['JTSSQ1MC']},
        {'offsets': 'formJson.0.JTSSQ2', 'value': storage['form_data']['previous']['JTSSQ2'] + '@#@' + storage['form_data']['previous']['JTSSQ2MC']},
        {'offsets': 'formJson.0.JTSSQ3', 'value': storage['form_data']['previous']['JTSSQ3'] + '@#@' + storage['form_data']['previous']['JTSSQ3MC']},
        {'offsets': 'formJson.0.JTJTDZ', 'value': storage['form_data']['previous']['JTJTDZ']},
        {'offsets': 'formJson.0.XJSSQ1', 'value': storage['form_data']['previous']['XJSSQ1'] + '@#@' + storage['form_data']['previous']['XJSSQ1MC']},
        {'offsets': 'formJson.0.XJSSQ2', 'value': storage['form_data']['previous']['XJSSQ2'] + '@#@' + storage['form_data']['previous']['XJSSQ2MC']},
        {'offsets': 'formJson.0.XJSSQ3', 'value': storage['form_data']['previous']['XJSSQ3'] + '@#@' + storage['form_data']['previous']['XJSSQ3MC']},
        {'offsets': 'formJson.0.JTDZ', 'value': storage['form_data']['previous']['JTDZ']},
        {'offsets': 'formJson.0.TBRQ', 'value': str(datetime.date.today())},
        {'offsets': 'formJson.0.BRTW', 'value': str(round(random.uniform(36.4, 37.0), 1))},
        {'offsets': 'formJson.0.FDYXM', 'value': storage['form_data']['previous']['FDYXM'] + '@#@' + storage['form_data']['previous']['FDYXM']},
        {'offsets': 'formJson.0.XH1', 'value': storage['user_info']['userId']},
        {'offsets': 'formJson.0.FQSJ', 'value': str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))},
        {'offsets': 'flowJson.0.id', 'value': storage['node_id']},
        {'offsets': 'flowJson.0.name', 'value': storage['user_info']['userId']},
        {'offsets': 'flowJson.0.title', 'value': storage['user_info']['userName']},
    ]

    
    for datum in data:
        print('[  OK  ]Compiling Form Data: ', datum['offsets'], end='')
        index = datum['offsets'].split('.')
        location = 'storage[\'form\']'
        for i in index:
            location += ('[' + i + ']' if i.isdigit() else '[\'' + i + '\']')
        loc = locals()
        exec(location + ' = ' + '\'' + datum['value'] + '\'', {'storage': storage}, loc)

        print(' ..... done')
    
    return

def submit_form(session):
    with open('trail.json', 'w', encoding='utf-8') as trail:
        json.dump(storage['form'], trail)

    url = 'http://one2020.xjtu.edu.cn/EIP/cooperative/sendCooperative.htm'

    print('[  OK  ]Submiting to: ', url, end='')
    # response = session.post(
    #     url,
    #     data=json.dumps(storage['form']),
    #     headers={
    #         'Content-Type': 'application/json'
    #     }
    # )

    print(' ..... done')
    return


if __name__ == "__main__": 
    print('[  OK  ]Creating Scheduler', end='')
    schedule.every().day.at("01:00").do(run)
    print(' ..... done')

    print('[  OK  ]Starting Scheduler ..... done')
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt as i:
            exit()
            print('[  OK  ]Exiting')
