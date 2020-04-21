import base64
import json
import re
import time
import requests

from Crypto.Cipher import AES

from config.config import config


def login():
    session = requests.session()
    timestamp = lambda: int(round(time.time() * 1000))

    # Goto Auth Page 前往认证页面，获取 Cookies
    url = 'https://org.xjtu.edu.cn/openplatform/oauth/authorizeCas?' + http_build_query({
        'state': 'xjdCas',
        'redirectUri': 'https://cas.xjtu.edu.cn?' + http_build_query({
            # 'service': 'http://ehall.xjtu.edu.cn'
            'TARGET': 'http://one2020.xjtu.edu.cn/EIP/caslogin.jsp'
        })
    })    
    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)

    # Check for Captcha Code 检查是否需要验证码
    url = 'https://org.xjtu.edu.cn/openplatform/g/admin/getIsShowJcaptchaCode?' + http_build_query({
        'userName': config('login.username'),
        '_': timestamp()
    })
    print(' ..... done')
    
    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)
    data = json.loads(response.text)
    print(' ..... done')

    url = 'https://org.xjtu.edu.cn/openplatform/g/admin/login'

    captcha = ''
    if data['data']:
        print('[ INFO ]Captcha Required, awaiting input')
        print('[  OK  ]Requesting Captcha', end='')
        # 获取验证码写入文件
        response = session.post(
            'https://org.xjtu.edu.cn/openplatform/g/admin/getJcaptchaCode',
            headers={
                'Content-Type': 'application/json;charset=UTF-8'
            }
        )
        data = json.loads(response.text)
        img = base64.b64decode(data['data'])
        with open('captcha.png', 'wb') as file:
            file.write(img)
        print(' ..... done')

        captcha = input('Captcha:')

    # 构造登陆数据
    
    print('[  OK  ]Building Login Info', end='')
    login_params = {
        'username': config('login.username'),
        'pwd': encrypt(config('login.password')),
        'loginType': 1,
        'jcaptchaCode': captcha
    }
    print(' ..... done')

    # 添加请求头
    login_headers = {
        'Content-Type': 'application/json;charset=utf-8',
    }

    # 请求登录
    print('[  OK  ]Requesting: ', url, end='')
    response = session.post(url, data=json.dumps(login_params), headers=login_headers)
    data = json.loads(response.text)
    if data['code'] != 0:
        print('\n[FAILED]Login Error: ', data)
        print('[  OK  ]Exiting')
        return False
    print(' ..... done')

    # 登陆成功后设置 Cookies
    session.cookies.set('open_Platform_User', str(data['data']['tokenKey']))
    session.cookies.set('memberId', str(data['data']['orgInfo']['memberId']))
    
    # 模拟 login.js 请求用户数据
    url = 'https://org.xjtu.edu.cn/openplatform/g/admin/getUserIdentity?' + http_build_query({
        'memberId': data['data']['orgInfo']['memberId'],
        '_': timestamp()
    })

    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)
    data = json.loads(response.text)
    print(' ..... done')

    # 请求重定向地址
    url = 'https://org.xjtu.edu.cn/openplatform/oauth/auth/getRedirectUrl?' + http_build_query({
        'userType': data['data'][0]['userType'],
        'personNo': data['data'][0]['personNo'],
        '_': timestamp()
    })

    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)
    data = json.loads(response.text)
    if data['code'] != 0:
        print('\n[FAILED]Login Error: ', data)
        return False
    print(' ..... done')
    
    redirect_url = data['data'].split('?')

    # Fllowing code for parsing redirect url
    params = {}
    for param in redirect_url[1].split('&'):
        tmp = param.split('=')
        params[tmp[0]] = tmp[1]

    url = redirect_url[0] + '/login?' + redirect_url[1]

    print('[  OK  ]Redirecting To: ', url, end='')
    response = session.get(url)
    data = response.text
    print(' ..... done')

    # 解析 HTML 中表单信息
    form_data = {
        'lt': re.search('\"LT-\S+\"', data).group().strip('"'),
        'org_code': re.search('\"orgCode\"  value=\"\S+\"', data).group().split('=')[1].strip('"'),
        'execution': re.search(r'(?<=name="execution" value=").*?(?=")', data).group(),
        'user_type': params['userType'],
        'user_employeeno': params['employeeNo']
    }

    # 请求 CAS 获取服务认证信息
    form_data = {
        'username': ' ',
        'password': ' ',
        'lt': form_data['lt'],
        'execution': form_data['execution'],
        'orgCode': form_data['org_code'],
        'usertype': form_data['user_type'],
        'userEmployeeno': form_data['user_employeeno'],
        '_eventId': 'submit'
    }

    print('[  OK  ]Requesting: ', url, end='')
    response = session.post(url, data=form_data)

    try:
        url = re.search(r'(?<=url=).*?(?=")', response.text).group()
    except AttributeError as e:
        print('\n[FAILED]Response Data Has No Redirect Information')
        print('[  OK  ]Writing to file: login_failed.html', end='')
        
        with open('login_failed.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(' ..... done')
        print('[  OK  ]Exiting')
        return False
    print(' ..... done')
    return url

def pad(text):
    text_length = len(text)
    amount_to_pad = AES.block_size - (text_length % AES.block_size)
    if amount_to_pad == 0:
        amount_to_pad = AES.block_size
    pad = chr(amount_to_pad)
    return text + pad * amount_to_pad

def encrypt(password):
    crypter = AES.new(
        config('login.public_key').encode('utf-8'),
        AES.MODE_ECB
    )

    encrypted_data = crypter.encrypt(pad(password).encode('utf-8'))    
    return str(base64.b64encode(encrypted_data), encoding='utf-8')

def http_build_query(parameters):
    query = []
    for (key, parameter) in parameters.items():
        clause = str(key) + '=' + str(parameter)
        query.append(clause)
    return '&'.join(query)
