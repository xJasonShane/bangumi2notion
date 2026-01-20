import os
import logging
from dotenv import load_dotenv
from exceptions import ConfigError
from constants import ConfigConstants


class Config:
    """配置管理类"""

    def __init__(self):
        """初始化配置"""
        load_dotenv()

        self.bangumi_username = os.getenv('BANGUMI_USERNAME')
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.log_level = os.getenv('LOG_LEVEL', ConfigConstants.DEFAULT_LOG_LEVEL).upper()
        self.enable_delete = self._parse_bool(os.getenv('ENABLE_DELETE', 'true'))
        self.sync_status = os.getenv('SYNC_STATUS', ConfigConstants.DEFAULT_SYNC_STATUS).lower()

        self.validate()

    def _parse_bool(self, value: str, default: bool = True) -> bool:
        """解析布尔配置值"""
        if value is None:
            return default
        return value.lower() in ['true', '1', 'yes', 'y']

    def validate(self) -> None:
        """验证配置完整性"""
        required_fields = {
            'BANGUMI_USERNAME': self.bangumi_username,
            'NOTION_TOKEN': self.notion_token,
            'NOTION_DATABASE_ID': self.notion_database_id
        }

        missing_fields = [field_name for field_name, field_value in required_fields.items() if not field_value]
        if missing_fields:
            raise ConfigError(f"缺少必要的环境变量: {', '.join(missing_fields)}")

        if self.log_level not in ConfigConstants.VALID_LOG_LEVELS:
            valid_levels = ', '.join(ConfigConstants.VALID_LOG_LEVELS)
            raise ConfigError(f"无效的LOG_LEVEL值: {self.log_level}，有效值为: {valid_levels}")

        if self.sync_status not in ConfigConstants.VALID_STATUSES:
            valid_statuses = ', '.join(ConfigConstants.VALID_STATUSES)
            raise ConfigError(f"无效的SYNC_STATUS值: {self.sync_status}，有效值为: {valid_statuses}")

    def __str__(self) -> str:
        """返回配置字符串表示"""
        return f"Config(\n" \
               f"  bangumi_username: {self.bangumi_username},\n" \
               f"  notion_token: {'***' if self.notion_token else None},\n" \
               f"  notion_database_id: {self.notion_database_id},\n" \
               f"  log_level: {self.log_level},\n" \
               f"  enable_delete: {self.enable_delete},\n" \
               f"  sync_status: {self.sync_status}\n" \
               f")"
