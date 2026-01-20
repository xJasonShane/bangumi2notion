"""统一常量管理模块"""


class BangumiConstants:
    """Bangumi相关常量"""

    BASE_URL = "https://api.bgm.tv/v0"
    DEFAULT_TIMEOUT = 10
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_RETRY_DELAY = 1
    USER_AGENT = "bangumi2notion/1.0.0"
    DEFAULT_LIMIT = 50

    WATCHING_STATUS_MAP = {
        1: "wish",
        2: "watching",
        3: "watched",
        4: "on_hold",
        5: "dropped"
    }

    AIR_STATUS_MAP = {
        1: "watching",
        2: "finished",
        3: "not_aired"
    }

    ANIME_TYPE = 1


class NotionConstants:
    """Notion相关常量"""

    WATCHING_STATUS_MAP = {
        "wish": "想看",
        "watching": "在看",
        "watched": "看过",
        "on_hold": "搁置",
        "dropped": "抛弃"
    }

    AIR_STATUS_MAP = {
        "watching": "连载中",
        "finished": "已完结",
        "not_aired": "未播出"
    }


class ConfigConstants:
    """配置相关常量"""

    VALID_STATUSES = ['all', 'watching', 'watched', 'wish', 'on_hold', 'dropped']
    VALID_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    DEFAULT_LOG_LEVEL = 'INFO'
    DEFAULT_SYNC_STATUS = 'all'
    DEFAULT_ENABLE_DELETE = True
