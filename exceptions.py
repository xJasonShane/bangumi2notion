"""统一异常管理模块"""


class BaseError(Exception):
    """基础异常类"""

    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.original_exception = original_exception

    def __str__(self) -> str:
        if self.original_exception:
            return f"{self.args[0]}: {self.original_exception}"
        return self.args[0]


class ConfigError(BaseError):
    """配置错误异常"""
    pass


class BangumiAPIError(BaseError):
    """Bangumi API请求错误"""
    pass


class NotionAPIError(BaseError):
    """Notion API请求错误"""
    pass


class SyncError(BaseError):
    """同步过程错误"""
    pass
