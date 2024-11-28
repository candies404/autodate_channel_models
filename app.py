import os
import sys
from typing import Optional, Tuple
import argparse

from dotenv import load_dotenv

from clients import BaseAPIClient, OneHubClient, OneAPIClient, NewAPIClient


def get_config() -> Tuple[str, str, str, str, int, str, float]:
    """
    获取配置信息
    :return: base_url, username, password, access_token, target_channel_status, client_type, delay_time
    """
    load_dotenv()

    base_url = os.getenv('API_BASE_URL')
    if base_url:
        base_url = base_url.rstrip('/')
    username = os.getenv('API_USERNAME')
    password = os.getenv('API_PASSWORD')
    access_token = os.getenv('API_ACCESS_TOKEN')
    target_channel_status = int(os.getenv('TARGET_CHANNEL_STATUS') or 0)
    client_type = os.getenv('CLIENT_TYPE', 'onehub')
    delay_time = float(os.getenv('DELAY_TIME') or 3.0)

    return base_url, username, password, access_token, target_channel_status, client_type, delay_time


def check_auth_config(base_url: str, username: str, password: str, access_token: str) -> bool:
    """
    检查认证配置是否有效
    :return: bool
    """
    if not base_url:
        print("❌ API_BASE_URL 未配置环境变量")
        return False

    if not access_token and (not username or not password):
        print("❌ 需要配置 API_ACCESS_TOKEN环境变量 或 API_USERNAME/API_PASSWORD环境变量")
        return False

    return True


def init_client(base_url: str, username: str, password: str, access_token: str, client_type: str = "onehub") -> \
        Optional[BaseAPIClient]:
    """
    初始化客户端并认证
    :param base_url: API基础地址
    :param username: 用户名
    :param password: 密码
    :param access_token: access_token
    :param client_type: 客户端类型 ("onehub", "oneapi", "newapi")
    :return: BaseAPIClient 实例
    """
    try:
        client_classes = {
            "onehub": OneHubClient,
            "oneapi": OneAPIClient,
            "newapi": NewAPIClient
        }

        client_class = client_classes.get(client_type.lower())
        if not client_class:
            print(f"❌ 未知的客户端类型: {client_type}")
            return None

        client = client_class(base_url, access_token)

        if access_token:
            print("使用 access token 认证...")
            if not client.check_login_status():
                print("❌ access token 验证失败")
                return None
        else:
            print("使用账号密码认证...")
            if not client.login(username, password):
                print("❌ 账号密码验证失败")
                return None

        return client

    except Exception as e:
        print(f"❌ 客户端初始化失败: {str(e)}")
        return None


def print_usage():
    """打印使用说明"""
    print("\n配置说明:")
    print("请在 .env 文件中配置以下参数:")
    print("- API_BASE_URL: API基础地址")
    print("- API_USERNAME: 用户名 (使用账号密码认证时必需)")
    print("- API_PASSWORD: 密码 (使用账号密码认证时必需)")
    print("- API_ACCESS_TOKEN: access token (可选，优先使用)")
    print("- TARGET_CHANNEL_STATUS: 目标渠道状态 (可选，默认0)")
    print("- DELAY_TIME: 更新渠道之间的随机休眠时间最大值 (可选，默认3.0秒)")
    print("- CLIENT_TYPE: 客户端类型 (可选，默认onehub)")
    print("\n目标渠道状态说明:")
    print("- 0: 所有状态")
    print("- 1: 启用")
    print("- 2: 手动关闭")
    print("- 3: 自动关闭")


def show_menu() -> Tuple[int, Optional[int]]:
    """
    显示交互式菜单
    :return: (选择的操作, 渠道ID)
    """
    print("\n" + "=" * 50)
    print("渠道更新工具")
    print("=" * 50)
    print("1. 批量更新所有渠道")
    print("2. 更新单个渠道")
    print("0. 退出程序")
    print("=" * 50)

    try:
        choice = input("请选择操作 (0-2): ").strip()
        if not choice.isdigit():
            print("❌ 请输入数字")
            return -1, None

        choice = int(choice)
        if choice not in [0, 1, 2]:
            print("❌ 无效的选择，请重新输入")
            return -1, None

        if choice == 2:
            channel_id = input("请输入渠道ID: ").strip()
            if not channel_id.isdigit():
                print("❌ 请输入数字")
                return -1, None
            return choice, int(channel_id)

        return choice, None

    except Exception as e:
        print(f"❌ 输入错误: {str(e)}")
        return -1, None


def main():
    """主函数"""
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="渠道更新工具")
    parser.add_argument("--auto", action="store_true", help="自动模式，直接更新所有渠道")
    args = parser.parse_args()

    # 获取配置
    base_url, username, password, access_token, target_channel_status, client_type, delay_time = get_config()

    # 检查配置
    if not check_auth_config(base_url, username, password, access_token):
        print_usage()
        sys.exit(1)  # 使用 sys.exit() 来确保正确的退出码

    # status自动关闭status为3，手动为2
    status_text_map = {
        0: "所有状态",
        1: "启用",
        2: "手动关闭",
        3: "自动关闭"
    }
    # 打印相关配置
    print(f'更新渠道之间的随机休眠时间最大值: {delay_time} 秒')
    print(f'需要更新的渠道状态: {status_text_map.get(target_channel_status)}')
    # 初始化客户端
    client = init_client(base_url, username, password, access_token, client_type)
    if not client:
        print("❌ 客户端初始化失败，程序退出")
        sys.exit(1)

    try:
        if args.auto:
            # 自动模式：直接更新所有渠道
            print("自动模式：更新所有渠道")
            client.batch_update_channels(delay_time, target_channel_status, mask_channel_name=True)
        else:
            # 交互模式：显示菜单
            while True:
                choice, channel_id = show_menu()

                if choice == 0:  # 退出程序
                    print("\n👋 感谢使用，再见！")
                    break
                elif choice == 1:  # 批量更新
                    client.batch_update_channels(delay_time, target_channel_status)
                elif choice == 2:  # 更新单个渠道
                    if channel_id is None:
                        print("❌ 请输入有效的渠道ID")
                        continue
                    client.update_single_channel(channel_id)

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
