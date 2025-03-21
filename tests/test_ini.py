from pathlib import Path

import pytest

from pytest_result_sender import plugin  # 导入配置文件

pytest_plugins = "pytester"  # 要使用pytester需要先声明；我是测试开发


@pytest.fixture(autouse=True)  # 每次用例执行前都会执行
def mock():
    # 创建一个干净的测试环境
    bak_data = plugin.data
    plugin.data = {"passed": 0, "failed": 0}
    print("-------------yield之前执行")

    yield
    print("-------------------yield之后执行")
    # 恢复测试环境
    plugin.data = bak_data


# 测试pytest.ini配置文件中send_when
@pytest.mark.parametrize("send_when", ["every", "on_fail"])
def test_send_when(send_when, pytester: pytest.Pytester, tmp_path: Path):
    """
    :param send_when: 参数
    :param pytester: 测试自己，运行自己
    :param tmp_path: 生成和保存一个临时的配置文件
    :return:
    """
    config_path = tmp_path.joinpath("pytest.ini")  # 创建一个临时的配置文件
    # 直接写入文本
    config_path.write_text(
        f"""
[pytest]
send_when = {send_when}
send_api = "http://baidu.com"
"""
    )

    # 断言： 配置加载成功
    config = pytester.parseconfig(config_path)  # 使用pytester加载配置文件，并赋值给变量
    assert config.getini("send_when") == send_when

    pytester.makepyfile(  # 构建场景，用例全部通过
        """
        def test_pass():
            ...
        """
    )

    pytester.runpytest("-c", str(config_path))  # 根据配置项执行用例

    # 如何断言，插件到底有没有发送结果
    print(plugin.data)
    if send_when == "every":
        assert plugin.data["send_done"] == 1
    else:
        assert plugin.data.get("send_done") is None


# 测试pytest.ini配置文件中send_api
@pytest.mark.parametrize("send_api", ["http://baidu.com", ""])
def test_send_api(send_api, pytester: pytest.Pytester, tmp_path: Path):
    config_path = tmp_path.joinpath("pytest.ini")  # 创建一个临时的配置文件
    # 直接写入文本
    config_path.write_text(
        f"""
[pytest]
send_when = 'every'
send_api = {send_api}
"""
    )

    # 断言： 配置加载成功
    config = pytester.parseconfig(config_path)  # 使用pytester加载配置文件，并赋值给变量
    assert config.getini("send_api") == send_api

    pytester.makepyfile(  # 构建场景，用例全部通过
        """
        def test_pass():
            ...
        """
    )

    pytester.runpytest("-c", str(config_path))  # 根据配置项执行用例

    # 如何断言，插件到底有没有发送结果
    print(plugin.data)
    if send_api:
        assert plugin.data["send_done"] == 1
    else:
        assert plugin.data.get("send_done") is None
