import random
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseAPIClient(ABC):
    """API客户端抽象基类"""

    def __init__(self, base_url: str, bearer_token: Optional[str] = None):
        """
        初始化客户端
        :param base_url: API基础地址
        :param bearer_token: Bearer token（可选）
        """
        self.base_url = base_url
        self.session = requests.session()
        self.bearer_token = bearer_token

        if bearer_token:
            self.session.headers.update({
                'Authorization': f'Bearer {bearer_token}'
            })

    @abstractmethod
    def check_login_status(self) -> bool:
        """测试登录状态是否有效"""
        pass

    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """登录接口"""
        pass

    @abstractmethod
    def get_channels_list(self, **kwargs) -> Optional[Dict[str, Any]]:
        """获取渠道列表"""
        pass

    @abstractmethod
    def get_channel_detail(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """获取渠道详情"""
        pass

    @abstractmethod
    def get_provider_models(self, channel_data: Dict[str, Any]) -> Optional[list]:
        """获取提供商支持的模型列表"""
        pass

    @abstractmethod
    def update_channel(self, channel_data: Dict[str, Any], new_models: str) -> bool:
        """更新渠道信息"""
        pass

    @abstractmethod
    def update_single_channel(self, channel_id: int, is_batch: bool = False, mask_channel_name: bool = False) -> bool:
        """更新单个渠道"""
        pass

    @abstractmethod
    def batch_update_channels(self, delay: float = 1.0, target_channel_status: int = 0,
                              mask_channel_name: bool = False) -> None:
        """批量更新渠道配置"""
        pass

    @staticmethod
    def _get_random_delay(max_delay: float = 1.0) -> float:
        """获取随机等待时间"""
        return random.uniform(max_delay * 0.1, max_delay)

    @staticmethod
    def _print_batch_update_summary(total_channels: int, success_count: int, fail_count: int) -> None:
        """打印批量更新摘要"""
        print(f"{'=' * 50}")
        print("批量更新统计:")
        print(f"批量更新: {total_channels}")
        print(f"更新成功: {success_count}")
        print(f"更新失败: {fail_count}")
        if total_channels > 0:
            print(f"完成率: {(success_count / total_channels) * 100:.1f}%")
        print(f"{'=' * 50}\n")
