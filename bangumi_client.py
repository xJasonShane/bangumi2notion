import requests
import time
import logging

logger = logging.getLogger(__name__)


class BangumiAPIError(Exception):
    """Bangumi API请求错误"""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception
    
    def __str__(self):
        if self.original_exception:
            return f"{self.args[0]}: {self.original_exception}"
        return self.args[0]


class BangumiClient:
    """Bangumi API客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.base_url = "https://api.bgm.tv/v0"
        self.timeout = 10
        self.retry_count = 3
        self.retry_delay = 1
    
    def _request(self, endpoint, params=None):
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
        headers = {
            "User-Agent": "bangumi2notion/1.0.0",
            "Accept": "application/json"
        }
        
        try:
            logger.debug(f"发送请求: {url}, 参数: {params}")
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise BangumiAPIError(f"Bangumi API请求失败: {url}", e) from e
    
    def _retry_request(self, endpoint, params=None):
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
                logger.warning(f"请求失败，将在 {self.retry_delay * (2 ** attempt)} 秒后重试 ({attempt + 1}/{self.retry_count})")
                time.sleep(self.retry_delay * (2 ** attempt))
    
    def get_user_collections(self, username):
        """获取用户追番记录
        
        Args:
            username: Bangumi用户名
            
        Returns:
            用户追番记录列表
        """
        endpoint = f"/users/{username}/collections"
        params = {
            "type": 1,  # 1表示动画
            "limit": 50,  # 每次请求返回50条
            "offset": 0
        }
        
        collections = []
        total = 0
        
        while True:
            data = self._retry_request(endpoint, params)
            collections.extend(data.get("data", []))
            
            # 获取总数
            if not total:
                total = data.get("total", 0)
            
            # 检查是否还有更多数据
            offset = params["offset"] + params["limit"]
            if offset >= total:
                break
            params["offset"] = offset
        
        logger.info(f"成功获取 {username} 的 {len(collections)} 条追番记录")
        return collections
    
    def get_subject_detail(self, subject_id):
        """获取番剧详细信息
        
        Args:
            subject_id: 番剧ID
            
        Returns:
            番剧详细信息
        """
        endpoint = f"/subjects/{subject_id}"
        return self._retry_request(endpoint)
    
    def parse_collection_data(self, collection):
        """解析收藏数据
        
        Args:
            collection: 原始收藏数据
            
        Returns:
            解析后的收藏数据
        """
        subject = collection.get("subject", {})
        collection_info = collection.get("collection", {})
        
        # 解析观看状态
        status_map = {
            1: "wish",      # 想看
            2: "watching",   # 在看
            3: "watched",    # 看过
            4: "on_hold",    # 搁置
            5: "dropped"     # 抛弃
        }
        
        # 解析播出状态
        air_status_map = {
            1: "watching",   # 连载中
            2: "finished",   # 已完结
            3: "not_aired"   # 未播出
        }
        
        return {
            "subject_id": subject.get("id"),
            "title": subject.get("name"),
            "title_cn": subject.get("name_cn"),
            "cover": subject.get("images", {}).get("large"),
            "score": subject.get("score"),
            "status": status_map.get(collection_info.get("status")),
            "type": subject.get("type"),
            "ep_status": collection_info.get("ep_status", 0),
            "total_episodes": subject.get("eps"),
            "air_date": subject.get("air_date"),
            "end_date": subject.get("end_date"),
            "official_site": subject.get("official_site"),
            "bangumi_url": f"https://bangumi.tv/subject/{subject.get('id')}",
            "air_status": air_status_map.get(subject.get("air_status"))
        }
