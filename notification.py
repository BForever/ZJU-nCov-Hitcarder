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
    chat_bot.send_markdown(title, text, at_dingtalk_ids = notification_config['at_dingtalk_ids'],
                           is_auto_at = notification_config['is_auto_at'])
    return chat_bot


def notification(record, config):
    # calculate msg
    data_str = datetime.datetime.now(tz = datetime.timezone(datetime.timedelta(hours = 8))).date().isoformat()
    title = '健康打卡结果报告'
    text = '[健康打卡链接](https://healthreport.zju.edu.cn/ncov/wap/default/index)\n'
    at_dingtalk_ids = []
    for rec in record.values():
#         if rec['last_time'] != data_str:
        at_dingtalk_ids.append(rec['ding_talk_id'])
        text += '- @' + rec['ding_talk_id'] + '自动打卡失败，报错信息：' + rec['msg'] + '\n'
    if not at_dingtalk_ids:
        return
    for rec in record.values():
        if rec['last_time'] == data_str:
            text += '- ' + rec['display_name'] + ' ' + rec['msg'] + '\n'

    for notification in config['notifications']:
        notification['at_dingtalk_ids'] = at_dingtalk_ids
        notification['is_auto_at'] = False
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
