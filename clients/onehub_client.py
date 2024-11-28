import time
from typing import Optional, Dict, Any

from .base_client import BaseAPIClient


class OneHubClient(BaseAPIClient):
    """OneHub API 客户端实现"""

    def check_login_status(self) -> bool:
        """测试登录状态是否有效"""
        print("检测登录状态中，请稍等...")
        # print("\n=== Session 信息 ===")
        # print("Headers:", dict(self.session.headers))
        # print("Cookies:", dict(self.session.cookies))
        # print("================\n")

        last_url = f"{self.base_url}/api/user/self"
        try:
            resp = self.session.get(last_url, verify=False)
            if resp.status_code == 200 and resp.json()["success"]:
                print(f"✅ 登录验证成功,当前用户：{resp.json()['data'].get('username', '未知用户')}")
                return True
            print(f"❌ 登录验证失败：{resp.json().get('message', '未知错误')}")
            return False
        except Exception as e:
            print(f"❌ 登录验证异常：{str(e)}")
            return False

    def login(self, username: str, password: str) -> bool:
        """登录接口"""
        # print("\n=== 登录前的 Session 信息 ===")
        # print("Headers:", dict(self.session.headers))
        # print("Cookies:", dict(self.session.cookies))
        # print("================\n")

        data = {
            "username": username,
            "password": password
        }
        last_url = f"{self.base_url}/api/user/login?turnstile="
        try:
            resp = self.session.post(last_url, json=data, verify=False)

            # print("\n=== 登录后的 Session 信息 ===")
            # print("Headers:", dict(self.session.headers))
            # print("Cookies:", dict(self.session.cookies))
            # print("Response Status:", resp.status_code)
            # print("Response Headers:", dict(resp.headers))
            # print("================\n")

            if resp.status_code == 200 and resp.json()["success"]:
                # print(f"登录成功：{self.base_url}")
                print(f"登录成功")
                return True
            print(f"登录失败：{resp.json().get('message', '未知错误')}")
            return False
        except Exception as e:
            print(f"登录异常：{str(e)}")
            return False

    def get_channels_list(self, **kwargs) -> Optional[Dict[str, Any]]:
        """获取渠道列表"""
        last_url = f"{self.base_url}/api/channel/"
        try:
            resp = self.session.get(last_url, params=kwargs, verify=False)
            if resp.status_code == 200 and resp.json()["success"]:
                return resp.json()["data"]
            print(f"获取渠道列表失败：{resp.json().get('message', '未知错误')}")
            return None
        except Exception as e:
            print(f"获取渠道列表异常：{str(e)}")
            return None

    def get_channel_detail(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """获取渠道详情"""
        last_url = f"{self.base_url}/api/channel/{channel_id}"
        try:
            resp = self.session.get(last_url, verify=False)
            if resp.status_code == 200 and resp.json()["success"]:
                return resp.json()["data"]
            print(f"获取渠道详情失败：{resp.json().get('message', '未知错误')}")
            return None
        except Exception as e:
            print(f"获取渠道详情异常：{str(e)}")
            return None

    def get_provider_models(self, channel_data: Dict[str, Any]) -> Optional[list]:
        """获取提供商支持的模型列表"""
        last_url = f"{self.base_url}/api/channel/provider_models_list"
        post_data = {**channel_data}
        post_data.update({
            "models": "",
            "model_mapping": "",
            "model_headers": "",
            "groups": ["default"],
            "is_edit": True
        })

        try:
            resp = self.session.post(last_url, json=post_data, verify=False)
            if resp.status_code == 200 and resp.json()["success"]:
                return resp.json()["data"]
            print(f"获取模型列表失败：{resp.json().get('message', '未知错误')}")
            return None
        except Exception as e:
            print(f"获取模型列表异常：{str(e)}")
            return None

    def update_channel(self, channel_data: Dict[str, Any], new_models: str) -> bool:
        """更新渠道信息"""
        last_url = f"{self.base_url}/api/channel/"
        update_data = {**channel_data}
        update_data.update({
            "models": new_models,
            "groups": ["default"],
            "is_edit": True
        })

        try:
            resp = self.session.put(last_url, json=update_data, verify=False)
            if resp.status_code == 200 and resp.json()["success"]:
                return True
            print(f"更新渠道失败：{resp.json().get('message', '未知错误')}")
            return False
        except Exception as e:
            print(f"更新渠道异常：{str(e)}")
            return False

    @staticmethod
    def mask_channel_name(name: str, should_mask: bool = False) -> str:
        """
        对渠道名称进行掩码处理
        :param name: 原始名称
        :param should_mask: 是否需要掩码
        :return: 处理后的名称
        """
        if not should_mask:
            return name

        if not name:
            return ""

        if len(name) <= 2:
            return '*' * len(name)

        return name[0] + '*' * (len(name) - 2) + name[-1]

    def update_single_channel(self, channel_id: int, is_batch: bool = False, mask_channel_name: bool = False) -> bool:
        """更新单个渠道"""
        if not is_batch:
            print(f"\n{'=' * 50}")
            print(f"开始更新单个渠道 (ID: {channel_id})")
            print(f"{'=' * 50}\n")

        # 添加渠道类型映射
        type_map = {
            1: "OpenAI",
            3: "Azure OpenAI",
            49: "GitHub",
            14: "Anthropic Claude"
        }

        try:
            print(f"[步骤1] 获取渠道 {channel_id} 详情...")
            channel_detail = self.get_channel_detail(channel_id)
            if not channel_detail:
                print(f"❌ 渠道 {channel_id} 详情获取失败")
                return False
            channel_name = channel_detail.get('name')
            display_name = self.mask_channel_name(channel_name, mask_channel_name)
            print(f"✅ 渠道名: {display_name} "
                  f"(类型: {type_map.get(channel_detail.get('type'))})")

            print(f"[步骤2] 获取渠道支持的模型列表...")
            models_list = self.get_provider_models(channel_detail)
            if not models_list:
                print(f"❌ 模型列表获取失败")
                return False
            print(f"✅ 获取成功: 共 {len(models_list)} 个模型")

            print(f"[步骤3] 替换新的模型...")
            new_models = ",".join(models_list)
            print(f"✅ 替换完成: {new_models[:50]}..." if len(new_models) > 50 else f"✅ 替换完成: {new_models}")

            print(f"[步骤4] 更新渠道信息...")
            update_success = self.update_channel(channel_detail, new_models)
            if update_success:
                print(f"✅ 渠道更新成功")
            else:
                print(f"❌ 渠道更新失败")
            return update_success

        except Exception as e:
            print(f"\n❌ 更新出错: {str(e)}")
            return False
        finally:
            if not is_batch:
                print(f"\n{'=' * 50}")
                print("单个渠道更新完成，注意查看上方的提示信息")
                print(f"{'=' * 50}\n")

    def batch_update_channels(self, delay: float = 1.0, target_channel_status: int = 0,
                              mask_channel_name: bool = False) -> None:
        """批量更新渠道配置"""
        # type=1为openai
        # type=3为Azure OpenAl
        # type=49为GitHub
        # type=14为Anthropic Claude

        page = 1
        size = 10
        success_count = 0
        fail_count = 0
        processed_count = 0
        total_channels = 0

        print(f"\n{'=' * 50}")
        print(f"开始批量更新渠道...")

        try:
            while True:
                channels_response = self.get_channels_list(
                    page=page,
                    size=size,
                    type=1,
                    status=target_channel_status
                )

                if not channels_response or "data" not in channels_response:
                    print("获取渠道列表失败")
                    return

                channel_list = channels_response.get("data", [])
                if not channel_list:
                    break

                total_channels = channels_response["total_count"]

                for channel in channel_list:
                    channel_id = channel["id"]
                    status = channel.get("status", 0)
                    status_text = {1: "启用", 2: "手动关闭", 3: "自动关闭"}.get(status, "未知状态")

                    processed_count += 1

                    print(f"\n{'-' * 30}")
                    print(f"正在执行第 {processed_count}/{total_channels} 次循环")
                    print(f"处理渠道 ID: {channel_id} (状态: {status_text})")

                    if self.update_single_channel(channel_id, is_batch=True, mask_channel_name=mask_channel_name):
                        success_count += 1
                    else:
                        fail_count += 1

                    progress = (processed_count / total_channels) * 100
                    print(f"\n当前进度: {progress:.1f}% "
                          f"({processed_count}/{total_channels}) "
                          f"[成功: {success_count}, 失败: {fail_count}]")

                    if processed_count < total_channels:
                        random_delay = self._get_random_delay(delay)
                        print(f"等待 {random_delay:.2f} 秒后继续...")
                        time.sleep(random_delay)

                if processed_count >= total_channels:
                    break

                page += 1
        except Exception as e:
            print(f"\n❌ 批量更新出错: {str(e)}")
        finally:
            self._print_batch_update_summary(total_channels, success_count, fail_count)
