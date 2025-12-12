import requests
import time
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class BangumiAPIError(Exception):
    """Bangumi API请求错误"""
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception
    
    def __str__(self) -> str:
        if self.original_exception:
            return f"{self.args[0]}: {self.original_exception}"
        return self.args[0]


class BangumiClient:
    """Bangumi API客户端"""
    
    # API配置常量
    BASE_URL = "https://api.bgm.tv/v0"
    DEFAULT_TIMEOUT = 10
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_RETRY_DELAY = 1
    USER_AGENT = "bangumi2notion/1.0.0"
    
    # 状态映射常量
    WATCHING_STATUS_MAP = {
        1: "wish",      # 想看
        2: "watching",   # 在看
        3: "watched",    # 看过
        4: "on_hold",    # 搁置
        5: "dropped"     # 抛弃
    }
    
    AIR_STATUS_MAP = {
        1: "watching",   # 连载中
        2: "finished",   # 已完结
        3: "not_aired"   # 未播出
    }
    
    def __init__(self, 
                 timeout: int = DEFAULT_TIMEOUT, 
                 retry_count: int = DEFAULT_RETRY_COUNT, 
                 retry_delay: int = DEFAULT_RETRY_DELAY):
        """初始化客户端
        
        Args:
            timeout: 请求超时时间（秒）
            retry_count: 请求失败重试次数
            retry_delay: 初始重试延迟（秒）
        """
        self.base_url = self.BASE_URL
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        # 初始化请求会话
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json"
        })
    
    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送API请求
        
        Args:
            endpoint: API端点
            params: 请求参数
            
        Returns:
            响应数据
            
        Raises:
            BangumiAPIError: API请求失败
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"发送请求: {url}, 参数: {params}")
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise BangumiAPIError(f"Bangumi API请求失败: {url}", e) from e
    
    def _retry_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """带重试的请求
        
        Args:
            endpoint: API端点
            params: 请求参数
            
        Returns:
            响应数据
            
        Raises:
            BangumiAPIError: 多次重试后请求仍然失败
        """
        for attempt in range(self.retry_count):
            try:
                return self._request(endpoint, params)
            except BangumiAPIError as e:
                if attempt == self.retry_count - 1:
                    raise
                
                delay = self.retry_delay * (2 ** attempt)
                logger.warning(f"请求失败，将在 {delay} 秒后重试 ({attempt + 1}/{self.retry_count})")
                time.sleep(delay)
        
        # 理论上不会执行到这里
        raise BangumiAPIError(f"多次重试后请求仍然失败: {endpoint}")
    
    def get_user_collections(self, username: str) -> List[Dict[str, Any]]:
        """获取用户追番记录
        
        Args:
            username: Bangumi用户名
            
        Returns:
            用户追番记录列表
        """
        logger.info(f"开始获取 {username} 的Bangumi追番记录")
        
        endpoint = f"/users/{username}/collections"
        params = {
            "type": 1,  # 1表示动画
            "limit": 50,  # 每次请求返回50条
            "offset": 0
        }
        
        collections = []
        total = 0
        page = 0
        
        while True:
            page += 1
            logger.debug(f"获取第 {page} 页追番记录")
            
            data = self._retry_request(endpoint, params)
            page_collections = data.get("data", [])
            collections.extend(page_collections)
            
            # 获取总数
            if not total:
                total = data.get("total", 0)
                logger.info(f"总共找到 {total} 条追番记录")
            
            # 检查是否还有更多数据
            offset = params["offset"] + params["limit"]
            if offset >= total or not page_collections:
                break
                
            params["offset"] = offset
        
        logger.info(f"成功获取 {username} 的 {len(collections)} 条追番记录")
        return collections
    
    def get_subject_detail(self, subject_id: int) -> Dict[str, Any]:
        """获取番剧详细信息
        
        Args:
            subject_id: 番剧ID
            
        Returns:
            番剧详细信息
        """
        logger.debug(f"获取番剧详情: {subject_id}")
        endpoint = f"/subjects/{subject_id}"
        return self._retry_request(endpoint)
    
    def parse_collection_data(self, collection: Dict[str, Any]) -> Dict[str, Any]:
        """解析收藏数据
        
        Args:
            collection: 原始收藏数据
            
        Returns:
            解析后的收藏数据
        """
        subject = collection.get("subject", {})
        collection_info = collection.get("collection", {})
        
        # 获取观看状态
        watch_status = collection_info.get("status")
        status = self.WATCHING_STATUS_MAP.get(watch_status)
        
        # 获取播出状态
        air_status = subject.get("air_status")
        air_status_text = self.AIR_STATUS_MAP.get(air_status)
        
        # 获取封面图片
        cover = subject.get("images", {}).get("large")
        if cover and cover.startswith("//"):
            cover = f"https:{cover}"
        
        # 构建Bangumi详情页URL
        subject_id = subject.get("id")
        bangumi_url = f"https://bangumi.tv/subject/{subject_id}" if subject_id else ""
        
        return {
            "subject_id": subject_id,
            "title": subject.get("name"),
            "title_cn": subject.get("name_cn"),
            "cover": cover,
            "score": subject.get("score"),
            "status": status,
            "type": subject.get("type"),
            "ep_status": collection_info.get("ep_status", 0),
            "total_episodes": subject.get("eps"),
            "air_date": subject.get("air_date"),
            "end_date": subject.get("end_date"),
            "official_site": subject.get("official_site"),
            "bangumi_url": bangumi_url,
            "air_status": air_status_text
        }
