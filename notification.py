# -*- coding: utf-8 -*-
import datetime
import json
import os
from dingtalkchatbot.chatbot import DingtalkChatbot


def send_msg(title, text, notification_type = 'ding_talk', **notification_config):
    if notification_type != 'ding_talk':
        print(f'do not support notification type {notification_type} now, ignore it')
        return
    chat_bot = DingtalkChatbot(notification_config['webhook'], secret = notification_config['secret'])
    chat_bot.send_markdown(title, text, at_mobiles = notification_config['at_mobiles'],)



def notification(record, config):
    # calculate msg
    data_str = datetime.datetime.now(tz = datetime.timezone(datetime.timedelta(hours = 8))).date().isoformat()
    title = '健康打卡结果报告'
    text = '[健康打卡链接](https://healthreport.zju.edu.cn/ncov/wap/default/index)\n'
    at_mobiles = []
    for rec in record.values():
        at_mobiles.append(rec['mobile'])
        if rec['last_time']==data_str:
            text += '- @' + rec['username'] + '自动打卡成功:' + rec['msg'] + '\n'
        else:
            text += '- @' + rec['username'] + '自动打卡失败:' + rec['msg'] + '\n'

    if not at_mobiles:
        return

    for notification in config['notifications']:
        notification['at_mobiles'] = at_mobiles
        send_msg(title, text, **notification)


def main():
    # load record
    record_path = os.path.join(os.path.dirname(__file__), 'record/record.json')
    if not os.path.exists(os.path.dirname(record_path)):
        os.makedirs(os.path.dirname(record_path))
    if os.path.exists(record_path):
        record = json.load(open(record_path))
    else:
        record = {}

    # load config
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.json')
    if os.path.exists(config_path):
        config = open(config_path).read()
    else:
        config = os.environ["CONFIG"]
    config = json.loads(config)

    notification(record, config)


if __name__ == "__main__":
    main()
