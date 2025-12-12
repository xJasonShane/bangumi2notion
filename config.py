import os
import logging
from dotenv import load_dotenv


class ConfigError(Exception):
    """配置错误异常"""
    pass


class Config:
    """配置管理类"""
    
    # 日志配置
    LOG_CONFIG = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    # 有效的同步状态
    VALID_STATUSES = ['all', 'watching', 'watched', 'wish', 'on_hold', 'dropped']
    
    def __init__(self):
        """初始化配置"""
        # 加载.env文件中的环境变量
        load_dotenv()
        
        # 从环境变量加载配置
        self.bangumi_username = os.getenv('BANGUMI_USERNAME')
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.sync_interval = self._parse_int(os.getenv('SYNC_INTERVAL', '86400'), default=86400)
        self.enable_delete = self._parse_bool(os.getenv('ENABLE_DELETE', 'true'))
        self.sync_status = os.getenv('SYNC_STATUS', 'all').lower()
        
        # 验证配置
        self.validate()
    
    def _parse_int(self, value, default=0):
        """解析整数配置值"""
        try:
            return int(value) if value is not None else default
        except ValueError:
            logging.warning(f"无效的整数配置值: {value}，使用默认值: {default}")
            return default
    
    def _parse_bool(self, value, default=True):
        """解析布尔配置值"""
        if value is None:
            return default
        return value.lower() in ['true', '1', 'yes', 'y']
    
    def validate(self):
        """验证配置完整性"""
        # 验证必填字段
        required_fields = {
            'BANGUMI_USERNAME': self.bangumi_username,
            'NOTION_TOKEN': self.notion_token,
            'NOTION_DATABASE_ID': self.notion_database_id
        }
        
        missing_fields = [field_name for field_name, field_value in required_fields.items() if not field_value]
        if missing_fields:
            raise ConfigError(f"缺少必要的环境变量: {', '.join(missing_fields)}")
        
        # 验证日志级别
        if self.log_level not in self.LOG_CONFIG:
            valid_levels = ', '.join(self.LOG_CONFIG.keys())
            raise ConfigError(f"无效的LOG_LEVEL值: {self.log_level}，有效值为: {valid_levels}")
        
        # 验证同步状态值
        if self.sync_status not in self.VALID_STATUSES:
            valid_statuses = ', '.join(self.VALID_STATUSES)
            raise ConfigError(f"无效的SYNC_STATUS值: {self.sync_status}，有效值为: {valid_statuses}")
    
    def get_log_level(self):
        """获取日志级别对应的logging模块常量"""
        return self.LOG_CONFIG.get(self.log_level, logging.INFO)
    
    def __str__(self):
        """返回配置字符串表示"""
        return f"Config(\n" \
               f"  bangumi_username: {self.bangumi_username},\n" \
               f"  notion_token: {'***' if self.notion_token else None},\n" \
               f"  notion_database_id: {self.notion_database_id},\n" \
               f"  log_level: {self.log_level},\n" \
               f"  sync_interval: {self.sync_interval},\n" \
               f"  enable_delete: {self.enable_delete},\n" \
               f"  sync_status: {self.sync_status}\n" \
               f")"
