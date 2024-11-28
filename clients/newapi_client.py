from typing import Optional, Dict, Any

from .base_client import BaseAPIClient


class NewAPIClient(BaseAPIClient):
    """NewAPI 客户端实现"""

    def check_login_status(self) -> bool:
        raise NotImplementedError("NewAPI 客户端尚未实现")

    def login(self, username: str, password: str) -> bool:
        raise NotImplementedError("NewAPI 客户端尚未实现")

    def get_channels_list(self, **kwargs) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("NewAPI 客户端尚未实现")

    def get_channel_detail(self, channel_id: int) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("NewAPI 客户端尚未实现")

    def get_provider_models(self, channel_data: Dict[str, Any]) -> Optional[list]:
        raise NotImplementedError("NewAPI 客户端尚未实现")

    def update_channel(self, channel_data: Dict[str, Any], new_models: str) -> bool:
        raise NotImplementedError("NewAPI 客户端尚未实现")

    def update_single_channel(self, channel_id: int, is_batch: bool = False, mask_channel_name: bool = False) -> bool:
        raise NotImplementedError("NewAPI 客户端尚未实现")

    def batch_update_channels(self, delay: float = 1.0, target_channel_status: int = 0,
                              mask_channel_name: bool = False) -> None:
        raise NotImplementedError("NewAPI 客户端尚未实现")
