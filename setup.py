import requests
import json
import re
import configparser
from shutil import copyfile
from getpass import getpass


def setup():
    print('Copying .env file')
    copyfile('.env.example', '.env')

    print('欢迎使用自动填报系统，下面将对项目进行基本配置')

    print('请配置账号信息:')
    username = input('Net-ID:')
    password = getpass('密码(No-Echo):')

    config = configparser.RawConfigParser()
    config.read('.env')
    config.set('login', 'username', username)
    config.set('login', 'password', password)

    with open('.env', 'w') as env:
        config.write(env)

    print('请选择运行模式：')
    print('[1]未返校')
    print('[2]已返校')

    mode = 0
    while mode not in ['1', '2']:
        mode = input(':')

    schedule = []
    if mode == '1':
        time = '25:61'
        while not re.match(r'(2[0-3]|[01]?[1-9]):([0-5]?[0-9])', time):
            time = input('请输入每天运行脚本的时间（建议选择在06:00后运行，当表单更新，需要时间更新模板）\n格式如："06:00" （无需双引号）:')
        schedule.append(time)

    elif mode == '2':
        time = '25:61'
        while (not re.match(r'(2[0-3]|[01]?[1-9]):([0-5]?[0-9])', time)) or not '11:00' > time > '06:00':
            time = input('请输入上午运行脚本的时间\n格式如："06:00" （无需双引号）:')
        schedule.append(time)

        time = '25:61'
        while (not re.match(r'(2[0-3]|[01]?[1-9]):([0-5]?[0-9])', time)) or not '17:00' > time > '12:00':
            time = input('请输入下午运行脚本的时间\n格式如："14:00" （无需双引号）:')
        schedule.append(time)

    with open('runtime/schedule.json', 'w') as file:
        json.dump(schedule, file)

    return mode


def download_json(mode):
    files = [
        'template.json',
        'queries.json',
        'assembly.json',
        'flow_id.json',
    ]

    base_url = 'https://secure.eeyes.xyz/reporter/' + ('returned' if mode == '2' else 'no-return') + '/'

    for file in files:
        print('Downloading ' + file + ' ..... ', end='')
        response = requests.get(base_url + file)
        with open('runtime/' + file, 'wb') as fp:
            fp.write(response.content)
        print('done')


if __name__ == '__main__':
    runtime_mode = setup()
    print('配置完成，正在下载模板文件')

    download_json(runtime_mode)
