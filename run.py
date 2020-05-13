import datetime
import json
import random
import re
import sys
import time

import requests
import schedule

from login import http_build_query, timestamp, login
from setup import download_json

storage = {}


def run():
    # 获取登陆链接
    url = login()

    # 请求登录链接，设置 Cookie
    session = requests.Session()
    session.get(url)

    # 检查文件更新
    check_for_update()

    # 从本地文件加载运行时数据
    runtime_data = load_runtime_data()

    # 获取用户信息
    get_user_info(session)

    # 获取自动注入信息
    auto_data = get_auto_data(session, runtime_data['queries'])

    # 获取提交 UUID
    uuid = get_form_uuid(session, runtime_data['flow_id'])

    # 获取事务节点 ID
    node_id = get_node_id(session)

    # 合成表单
    form_data = assemble_form(
        template=runtime_data['template'],
        auto_data=auto_data,
        assembly=runtime_data['assembly'],
        uuid=uuid,
        node_id=node_id
    )

    # 提交表单
    submit_form(session, form_data)

    return True


def get_form_uuid(session, flow_id):
    window_id = random.randint(0, 10000)
    t = random.randint(0, 1000000)

    url = 'http://one2020.xjtu.edu.cn/EIP/cooperative/openCooperative.htm?' + http_build_query({
        'flowId': flow_id,
        '_t': t,
        '_winid': window_id
    })

    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)
    uuid = re.search(r'var uuid = \'(.*)\';', response.text).group(1)
    print(' ..... done')
    return uuid


def get_user_info(session):
    url = 'http://one2020.xjtu.edu.cn/EIP/api/getUserAttribute.htm'

    print('[  OK  ]Requesting: ', url, end='')
    response = session.post(url)
    storage['user_info'] = json.loads(response.text)
    print(' ..... done')

    return


def get_auto_data(session, queries):
    base_url = 'http://one2020.xjtu.edu.cn/EIP/queryservice/query.htm'

    storage['form_data'] = {}
    data = {}
    for query in queries:
        url = base_url + '?' + http_build_query({
            'snumber': query['snumber'],
            query['id_key']: storage['user_info']['userId'],
            '_': timestamp()
        })

        print('[  OK  ]Requesting: ', url, end='')
        response = session.get(url)
        data[query['name']] = json.loads(response.text)[0]
        print(' ..... done')

    return data


def get_node_id(session):
    url = 'http://one2020.xjtu.edu.cn/EIP/flowNode/createNodeIdByNum.htm'

    print('[  OK  ]Requesting: ', url, end='')
    response = session.post(url, {'num': 1})
    node_id = json.loads(response.text)[0]
    print(' ..... done')

    return node_id


def load_runtime_data():
    files = [
        {'name': './runtime/queries.json', 'mode': 'r', 'key': 'queries'},
        {'name': './runtime/flow_id.json', 'mode': 'r', 'key': 'flow_id'},
        {'name': './runtime/template.json', 'mode': 'r', 'key': 'template'},
        {'name': './runtime/assembly.json', 'mode': 'r', 'key': 'assembly'},
    ]

    data = {}
    for file in files:
        print('[  OK  ]Loading Model from: ', file['name'], end='')
        with open(file['name'], 'r', encoding='utf-8') as read:
            datum = json.load(read)

        data[file['key']] = datum
        print(' ..... done')

    return data


def assemble_form(template, auto_data, assembly, uuid, node_id):
    for instruction in assembly:
        print('[  OK  ]Assembling Form Data: ', instruction['offsets'], end='')
        index = instruction['offsets'].split('.')
        location = 'template'
        for i in index:
            location += ('[' + i + ']' if i.isdigit() else '[\'' + i + '\']')
        loc = locals()
        gol = globals()
        exec('value = ' + instruction['value'], gol, loc)
        exec(location + ' = value', loc)

        print(' ..... done')

    return template


def submit_form(session, form_data):
    with open('trail.json', 'w', encoding='utf-8') as trail:
        json.dump(form_data, trail)

    url = 'http://one2020.xjtu.edu.cn/EIP/cooperative/sendCooperative.htm'

    print('[  OK  ]Submitting to: ', url, end='')

    form = {}
    for (key, value) in form_data.items():
        if value is None:
            form[key] = value
        elif isinstance(value, str):
            form[key] = value
        else:
            form[key] = json.dumps(value)

    response = session.post(url, form)

    data = json.loads(response.text)

    if data['code'] != '200':
        print('\n[FAILED]Submit Error: ', data['desc'])
        return False

    print(' ..... done')
    print('[  OK  ]Response: ', data['desc'])
    return


def load_schedules():
    import os

    if not os.path.exists('./runtime/schedule.json'):
        print('[FAILED]Schedules File Not Found, Please run setup tool to create')

    with open('./runtime/schedule.json') as file:
        schedule_list = json.load(file)

    return schedule_list


def check_for_update():
    with open('./runtime/mode', 'r') as mode_file:
        mode = mode_file.read()

    print('[  OK  ]Checking for update.', end='')

    with open('./runtime/version', 'r') as version_file:
        current = version_file.read()
    print(' Current Version: ', current.strip('\n'), end='.')

    response = requests.get(
        'https://secure.eeyes.xyz/reporter/' + ('no-return' if mode == '1' else 'returned') + '/version'
    )
    latest = response.text
    print(' Latest Version: ', latest.strip('\n'), end='.')

    if current == latest:
        print(' Not Updating ..... done')
    else:
        print(' Updating ..... done')
        download_json(mode)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--run-immediately':
        print('[  OK  ]Starting Immediately ..... done')
        run()
        exit(0)

    schedules = load_schedules()

    print('[  OK  ]Creating Scheduler', end='')
    for single_schedule in schedules:
        schedule.every().day.at(single_schedule).do(run)
    print(' ..... done')

    print('[  OK  ]Starting Scheduler ..... done')
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt as i:
            exit()
            print('[  OK  ]Exiting')
