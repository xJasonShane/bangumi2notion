import os
from dotenv import load_dotenv


class ConfigError(Exception):
    """配置错误异常"""
    pass


class Config:
    """配置管理类"""
    
    def __init__(self):
        """初始化配置"""
        # 加载.env文件中的环境变量
        load_dotenv()
        
        # 从环境变量加载配置
        self.bangumi_username = os.getenv('BANGUMI_USERNAME')
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.sync_interval = int(os.getenv('SYNC_INTERVAL', '86400'))
        self.enable_delete = os.getenv('ENABLE_DELETE', 'true').lower() == 'true'
        self.sync_status = os.getenv('SYNC_STATUS', 'all')  # all, watching, watched, wish, on_hold, dropped
        
        # 验证配置
        self.validate()
    
    def validate(self):
        """验证配置完整性"""
        required_fields = [
            ('BANGUMI_USERNAME', self.bangumi_username),
            ('NOTION_TOKEN', self.notion_token),
            ('NOTION_DATABASE_ID', self.notion_database_id)
        ]
        
        missing_fields = [field_name for field_name, field_value in required_fields if not field_value]
        if missing_fields:
            raise ConfigError(f"缺少必要的环境变量: {', '.join(missing_fields)}")
        
        # 验证同步状态值
        valid_statuses = ['all', 'watching', 'watched', 'wish', 'on_hold', 'dropped']
        if self.sync_status not in valid_statuses:
            raise ConfigError(f"无效的SYNC_STATUS值: {self.sync_status}，有效值为: {', '.join(valid_statuses)}")
    
    def __str__(self):
        """返回配置字符串表示"""
        return f"Config(\n" \
               f"  bangumi_username: {self.bangumi_username},\n" \
               f"  notion_token: {'***' if self.notion_token else None},\n" \
               f"  notion_database_id: {self.notion_database_id},\n" \
               f"  log_level: {self.log_level},\n" \
               f"  sync_interval: {self.sync_interval}\n" \
               f")"
