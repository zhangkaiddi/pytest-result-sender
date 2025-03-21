import json
from datetime import datetime, timedelta

import pytest
import requests

data = {"passed": 0, "failed": 0}


def pytest_addoption(parser):
    # 识别pytest.ini文件内容
    parser.addini(
        "send_when",
        help="什么时候发送，every表示每次都发送 或者 on_fail表示只有失败才发送",
    )
    parser.addini("send_api", help="发送到哪里")


def pytest_configure(config: pytest.Config):
    # 配置加载完毕后执行，所有测试用例执行前执行
    data["start_time"] = datetime.now()
    print(f"{datetime.now()} pytest开始执行")

    # 读取配置文件中的send_when 和 send_api
    data["send_when"] = config.getini("send_when")
    data["send_api"] = config.getini("send_api")


def pytest_collection_finish(session: pytest.Session):
    # 用例加载完成之后执行，包含了全部用例
    data["total"] = len(session.items)
    print(f"用例总数={data['total']}")


def pytest_runtest_logreport(report: pytest.TestReport):
    # 每个用例执行时调用
    if report.when == "call":
        print("本次用例的执行结果：", report.outcome)
        data[report.outcome] += 1


def pytest_unconfigure():
    # 配置卸载完毕后执行，所有测试用例执行后执行
    data["end_time"] = datetime.now()
    print(f"{datetime.now()} pytest结束执行")

    data["duration"] = data["end_time"] - data["start_time"]  # 获取运行时长
    data["pass_ratio"] = data["passed"] / data["total"] * 100  # 获取成功率
    data["pass_ratio"] = f"{data['pass_ratio']:.2f}%"

    send_result()


def send_result():
    if data["send_when"] == "on_fail" and data["failed"] == 0:
        # 如果配置失败才发送，但实际没有失败，则不发送
        print("不发送1")
        return

    if not data["send_api"]:
        # 如果没有配置api地址，不发送
        print("不发送2")
        return

    # 飞书群机器人发送通知
    # 替换为你的飞书群机器人的 Webhook URL
    webhook_url = data["send_api"]
    print(webhook_url)
    # 要发送的消息内容
    message = f"""
       pytest自动化测试结果
           测试时间： {data["end_time"]} 
           用例数量：{data['total']} 
           执行时长： {data["duration"]}  
           测试通过：<font color="green"> {data["pass_ratio"]} </font> 
           测试失败：<font color="red"> {data["failed"]} </font> 
           测试通过率：{data["pass_ratio"]}
           测试报告地址： http://www.baidu.com
       """

    headers = {"Content-Type": "application/json"}

    # Markdown 类型消息
    datas = {
        "msg_type": "interactive",
        "card": {
            "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": message}}]
        },
    }
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(datas))
        if response.status_code == 200:
            print("消息发送成功")
        else:
            print(
                f"消息发送失败，状态码: {response.status_code}, 响应内容: {response.text}"
            )
    except Exception:
        print("失败了耶")
        pass

    data["send_done"] = 1  # 发送成功
