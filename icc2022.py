# -*- coding: utf-8 -*-
"""
cron: 2 0 0 * * *
new Env('ICC2022');
"""

import json
from sendNotify import send
import requests
import re
import os
import sys
import time
requests.packages.urllib3.disable_warnings()

def start(cookie):
    max_retries = 20
    retries = 0
    msg = ""
    while retries < max_retries:
        try:
            msg += "第{}次执行签到\n".format(str(retries+1))
            sign_in_url = "https://www.icc2022.com/attendance.php"
            headers = {
                'Cookie': cookie,
                'authority': 'www.icc2022.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'zh-CN,zh;q=0.9,und;q=0.8',
                'referer': 'https://www.icc2022.com/',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            rsp = requests.get(url=sign_in_url, headers=headers, timeout=15, verify=False)
            
            rsp_text = rsp.text
            success = False
            if "签到已得" in rsp_text:
                msg += '已经签到过了，不再重复签到!\n'
                success = True
            elif "这是您的第" in rsp_text:
                msg += '签到成功!\n'
                # 定义正则表达式模式
                pattern = r'这是您的第 <b>(\d+)</b>[\s\S]*?今日签到排名：<b>(\d+)</b>'
                # 使用正则表达式进行匹配
                result = re.search(pattern, rsp_text)
                # 剔除多余字符
                result.replace("<b>", "")
                result.replace("点击白色背景的圆点进行补签。", "")
                msg += result
                success = True
            elif "https://www.gov.cn/" in rsp_text:
                msg += "Cookie值错误!响应跳转到第三方网站,请检查网站cookie值"
            elif "503 Service Temporarily" in rsp_text or "502 Bad Gateway" in rsp_text:
                msg += "服务器异常！\n"
            else:
                msg += "未知异常!\n"
                msg += rsp_text + '\n'
            
            if success:
                print("签到结果: ",msg)
                send("ICC2022 签到结果", msg)
                break  # 成功执行签到，跳出循环
            elif retries >= max_retries:
                print("达到最大重试次数，签到失败。")
                send("ICC2022 签到结果", msg)
                break
            else:
                retries += 1
                print("等待20秒后进行重试...")
                time.sleep(20)
        except Exception as e:
            print("签到失败，失败原因:"+str(e))
            send("ICC2022 签到结果", str(e))
            retries += 1
            if retries >= max_retries:
                print("达到最大重试次数，签到失败。")
                break
            else:
                print("等待20秒后进行重试...")
                time.sleep(20)

if __name__ == "__main__":
    cookie = os.getenv("ICC2022_COOKIE")
    start(cookie)
