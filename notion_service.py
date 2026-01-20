from notion_client import Client
import logging
import re
from typing import Dict, List, Optional, Any
from exceptions import NotionAPIError

logger = logging.getLogger(__name__)


class NotionService:
    """Notion API服务"""
    
    def __init__(self, token: str, database_id: str):
        """初始化客户端
        
        Args:
            token: Notion API密钥
            database_id: 目标数据库ID
        """
        self.token = token
        self.database_id = database_id
        
        try:
            self.client = Client(auth=token)
            logger.info(f"Notion客户端初始化成功")
        except Exception as e:
            logger.error(f"Notion客户端初始化失败: {e}")
            raise NotionAPIError(f"Notion客户端初始化失败", e) from e
    
    def get_database(self) -> Dict[str, Any]:
        """获取数据库信息

        Returns:
            数据库信息
        """
        try:
            logger.debug(f"获取数据库信息: {self.database_id}")
            return self.client.databases.retrieve(database_id=self.database_id)
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            raise NotionAPIError(f"获取Notion数据库信息失败: {self.database_id}", e) from e
    
    def query_database(self, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """查询数据库内容

        Args:
            filter: 查询过滤器

        Returns:
            数据库中的页面列表
        """
        try:
            logger.debug(f"查询数据库: {self.database_id}, 过滤器: {filter}")
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter
            )
            pages = response.get("results", [])
            
            # 处理分页
            page = 0
            while response.get("has_more"):
                page += 1
                logger.debug(f"查询第 {page} 页数据")
                response = self.client.databases.query(
                    database_id=self.database_id,
                    filter=filter,
                    start_cursor=response.get("next_cursor")
                )
                pages.extend(response.get("results", []))
            
            logger.info(f"成功查询到 {len(pages)} 条记录")
            return pages
        except Exception as e:
            logger.error(f"查询数据库失败: {e}")
            raise NotionAPIError(f"查询Notion数据库失败: {self.database_id}", e) from e
    
    def create_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新页面

        Args:
            page_data: 页面数据

        Returns:
            创建的页面信息
        """
        try:
            title = page_data.get('properties', {}).get('标题', {}).get('title', [{}])[0].get('text', {}).get('content', 'Unknown')
            logger.debug(f"创建新页面: {title}")
            return self.client.pages.create(parent={"database_id": self.database_id}, **page_data)
        except Exception as e:
            logger.error(f"创建页面失败: {e}")
            raise NotionAPIError(f"创建Notion页面失败", e) from e
    
    def update_page(self, page_id: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新页面

        Args:
            page_id: 页面ID
            page_data: 页面数据

        Returns:
            更新后的页面信息
        """
        try:
            logger.debug(f"更新页面: {page_id}")
            return self.client.pages.update(page_id=page_id, **page_data)
        except Exception as e:
            logger.error(f"更新页面失败: {e}")
            raise NotionAPIError(f"更新Notion页面失败: {page_id}", e) from e
    
    def get_existing_items(self) -> Dict[int, Dict[str, Any]]:
        """获取现有番剧记录

        Returns:
            现有番剧记录字典，key为subject_id，value为页面信息
        """
        logger.info("获取现有番剧记录")
        pages = self.query_database()
        existing_items = {}
        
        for page in pages:
            # 从Bangumi链接中提取subject_id
            bangumi_url = page.get("properties", {}).get("Bangumi链接", {}).get("url", "")
            subject_id = self._extract_subject_id(bangumi_url)
            
            if subject_id:
                existing_items[subject_id] = page
            else:
                logger.warning(f"无法从链接中提取subject_id: {bangumi_url}")
        
        logger.info(f"获取到 {len(existing_items)} 条现有番剧记录")
        return existing_items
    
    def _extract_subject_id(self, bangumi_url: str) -> Optional[int]:
        """从Bangumi链接中提取subject_id
        
        Args:
            bangumi_url: Bangumi详情页URL
            
        Returns:
            subject_id，如果无法提取则返回None
        """
        match = re.search(r"subject/(\d+)", bangumi_url)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                logger.warning(f"无效的subject_id格式: {match.group(1)}")
        return None
