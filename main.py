# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
import time

import requests
from notification import notification


class DaKa(object):
    """Hit card class

    Attributes:
        username: (str) 浙大统一认证平台用户名（一般为学号）
        password: (str) 浙大统一认证平台密码
        login_url: (str) 登录url
        base_url: (str) 打卡首页url
        save_url: (str) 提交打卡url
        self.headers: (dir) 请求头
        sess: (requests.Session) 统一的session
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_url = "https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex"
        self.base_url = "https://healthreport.zju.edu.cn/ncov/wap/default/index"
        self.save_url = "https://healthreport.zju.edu.cn/ncov/wap/default/save"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            'Connection': 'close'
        }
        self.sess = requests.Session()
        requests.adapters.DEFAULT_RETRIES = 5

    def login(self):
        """Login to ZJU platform."""
        res = self.sess.get(self.login_url, headers = self.headers, timeout = 60)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(url = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey', headers = self.headers, timeout = 60).json()
        n, e = res['modulus'], res['exponent']
        encrypt_password = self._rsa_encrypt(self.password, e, n)

        data = {
            'username': self.username,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit'
        }
        res = self.sess.post(url = self.login_url, data = data, headers = self.headers, timeout = 60)

        # check if login successfully
        if '统一身份认证' in res.content.decode():
            raise LoginError('登录失败，请核实账号密码重新登录')
        return self.sess

    def post(self):
        """Post the hit card info."""
        res = self.sess.post(self.save_url, data = self.info, headers = self.headers, timeout = 60)
        return json.loads(res.text)

    def get_date(self):
        """Get current date"""
        today = datetime.date.today()
        return "%4d%02d%02d" % (today.year, today.month, today.day)

    def get_info(self, html = None):
        """Get hitcard info, which is the old info with updated new time."""
        if not html:
            res = self.sess.get(self.base_url, headers = self.headers, timeout = 60)
            html = res.content.decode()

        try:
            old_infos = re.findall(r'oldInfo: ({[^\n]+})', html)
            old_infos = old_infos if len(old_infos) != 0 else re.findall(r'def = ({[^\n]+})', html)
            if len(old_infos) != 0:
                old_info = json.loads(old_infos[0])
            else:
                raise RegexMatchError("未发现缓存信息，请先至少手动成功打卡一次再运行脚本")

            new_info_tmp = json.loads(re.findall(r'def = ({[^\n]+})', html)[0])
            new_id = new_info_tmp['id']
            name = re.findall(r'realname: "([^\"]+)",', html)[0]
            number = re.findall(r"number: '([^\']+)',", html)[0]
        except IndexError as err:
            raise RegexMatchError('Relative info not found in html with regex: ' + str(err))
        except json.decoder.JSONDecodeError as err:
            raise DecodeError('JSON decode error: ' + str(err))

        new_info = old_info.copy()
        new_info['id'] = new_id
        new_info['name'] = name
        new_info['number'] = number
        new_info["date"] = self.get_date()
        new_info["created"] = round(time.time())
        # form change
        new_info['jrdqtlqk[]'] = 0
        new_info['jrdqjcqk[]'] = 0
        new_info['sfsqhzjkk'] = 1  # 是否申领杭州健康码
        new_info['sqhzjkkys'] = 1  # 杭州健康吗颜色，1:绿色 2:红色 3:黄色
        new_info['sfqrxxss'] = 1  # 是否确认信息属实
        new_info['jcqzrq'] = ""
        new_info['gwszdd'] = ""
        new_info['szgjcs'] = ""
        self.info = new_info
        return new_info

    def _rsa_encrypt(self, password_str, e_str, M_str):
        password_bytes = bytes(password_str, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16)
        M_int = int(M_str, 16)
        result_int = pow(password_int, e_int, M_int)
        return hex(result_int)[2:].rjust(128, '0')


# Exceptions 
class LoginError(Exception):
    """Login Exception"""
    pass


class RegexMatchError(Exception):
    """Regex Matching Exception"""
    pass


class DecodeError(Exception):
    """JSON Decode Exception"""
    pass


def hit_card(username, password):
    """Hit card process

    Arguments:
        username: (str) 浙大统一认证平台用户名（一般为学号）
        password: (str) 浙大统一认证平台密码
    """

    print("[Start Time] %s" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🚌 打卡任务启动")
    print('正在新建打卡实例...')
    dk = DaKa(username, password)
    print('已新建打卡实例')

    print('登录到浙大统一身份认证平台...')
    try:
        dk.login()
        print('已登录到浙大统一身份认证平台')
    except Exception as err:
        msg = str(err)
        print(msg)
        return False, msg

    print('正在获取个人信息...')
    try:
        dk.get_info()
        print('%s %s同学, 你好~' % (dk.info['number'], dk.info['name']))
    except Exception as err:
        msg = '获取信息失败，请手动打卡，更多信息: ' + str(err)
        print(msg)
        return False, msg

    print('正在为您打卡...')
    try:
        res = dk.post()
        info = {'date': dk.info['date'], 'area': dk.info['area']}
        msg = res['m'] + f'，本次打卡信息：{info}'
        print(msg)
        return res['e'] == 0 or res['e'] == 1, msg
    except:
        msg = '数据提交失败'
        print(msg)
        return False, msg


def main():
    # load config
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.json')
    if os.path.exists(config_path):
        config = open(config_path).read()
    else:
        config = os.environ["CONFIG"]
    config = json.loads(config)
    random.shuffle(config['users'])

    # hit card
    record = {}
    data_str = datetime.datetime.now(tz = datetime.timezone(datetime.timedelta(hours = 8))).date().isoformat()
    for i, item in enumerate(config['users']):
        success, msg = hit_card(item['username'], item['password'])
        record[item['username']] = {'last_time': None, 'msg': '', 'display_name': item['display_name'],
                                    'ding_talk_id': item['ding_talk_id']}
        record[item['username']]['msg'] = msg
        if success:
            record[item['username']]['last_time'] = data_str
        if i < len(config['users']) - 1:
            sleep_time = 10
            print('睡眠 %d s' % sleep_time)
            time.sleep(sleep_time)

    # dump record
    notification(record, config)


if __name__ == "__main__":
    main()
