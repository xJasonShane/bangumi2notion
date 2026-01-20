import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from exceptions import SyncError
from constants import NotionConstants

logger = logging.getLogger(__name__)


class SyncManager:
    """同步管理器"""

    def __init__(self, bangumi_client, notion_client, config):
        """初始化同步管理器

        Args:
            bangumi_client: BangumiClient实例
            notion_client: NotionService实例
            config: Config实例
        """
        self.bangumi_client = bangumi_client
        self.notion_client = notion_client
        self.config = config

        logger.info("同步管理器初始化成功")
        logger.debug(f"同步配置: {config}")
    
    def sync(self, dry_run: bool = False) -> Dict[str, int]:
        """执行同步流程

        Args:
            dry_run: 是否为模拟运行，不实际修改Notion数据库

        Returns:
            同步结果统计
        """
        logger.info("开始同步Bangumi追番记录到Notion...")
        
        try:
            # 1. 获取Bangumi数据
            bangumi_data = self.get_bangumi_data()
            
            # 2. 获取Notion数据
            notion_data = self.get_notion_data()
            
            # 3. 对比数据，生成操作列表
            operations = self.compare_data(bangumi_data, notion_data)
            
            # 4. 执行同步操作
            if dry_run:
                logger.info("模拟运行模式，不会实际修改Notion数据库")
                self._log_operations(operations)
            else:
                self.execute_sync(operations)
            
            logger.info("同步完成")
            return {
                "total_bangumi_items": len(bangumi_data),
                "total_notion_items": len(notion_data),
                "add_count": len(operations.get("add", [])),
                "update_count": len(operations.get("update", [])),
                "delete_count": len(operations.get("delete", []))
            }
        except Exception as e:
            logger.error(f"同步过程中发生错误: {e}")
            raise SyncError(f"同步过程中发生错误", e) from e
    
    def get_bangumi_data(self) -> Dict[int, Dict[str, Any]]:
        """获取Bangumi数据

        Returns:
            解析后的Bangumi追番记录字典，key为subject_id
        """
        logger.info(f"获取 {self.config.bangumi_username} 的Bangumi追番记录")
        collections = self.bangumi_client.get_user_collections(self.config.bangumi_username)
        
        bangumi_data = {}
        for collection in collections:
            parsed_data = self.bangumi_client.parse_collection_data(collection)
            subject_id = parsed_data.get("subject_id")
            
            # 根据sync_status过滤记录
            if subject_id:
                status = parsed_data.get("status")
                if self.config.sync_status == 'all' or self.config.sync_status == status:
                    bangumi_data[subject_id] = parsed_data
                else:
                    logger.debug(f"跳过记录: {parsed_data.get('title_cn') or parsed_data.get('title')} (状态: {status})")
        
        logger.info(f"成功解析 {len(bangumi_data)} 条Bangumi追番记录，过滤条件: {self.config.sync_status}")
        return bangumi_data
    
    def get_notion_data(self) -> Dict[int, Dict[str, Any]]:
        """获取Notion数据

        Returns:
            现有番剧记录字典，key为subject_id
        """
        return self.notion_client.get_existing_items()
    
    def compare_data(self,
                    bangumi_data: Dict[int, Dict[str, Any]],
                    notion_data: Dict[int, Dict[str, Any]]) -> Dict[str, List[Any]]:
        """对比数据，生成操作列表

        Args:
            bangumi_data: Bangumi追番记录字典
            notion_data: Notion现有记录字典

        Returns:
            操作列表，包含add、update、delete三个字段
        """
        logger.info("对比Bangumi和Notion数据")
        logger.debug(f"Bangumi数据条数: {len(bangumi_data)}, Notion数据条数: {len(notion_data)}")
        
        operations = {
            "add": [],      # Bangumi有但Notion没有的记录
            "update": [],   # Bangumi和Notion都有但字段不同的记录
            "delete": []    # Notion有但Bangumi没有的记录
        }
        
        # 找出需要添加的记录
        for subject_id, bangumi_item in bangumi_data.items():
            if subject_id not in notion_data:
                operations["add"].append(bangumi_item)
                title = bangumi_item.get("title_cn") or bangumi_item.get("title")
                logger.debug(f"需要添加: {title} (ID: {subject_id})")
        
        # 找出需要更新的记录
        for subject_id, bangumi_item in bangumi_data.items():
            if subject_id in notion_data:
                notion_item = notion_data[subject_id]
                if self._need_update(bangumi_item, notion_item):
                    operations["update"].append({
                        "bangumi_item": bangumi_item,
                        "notion_item": notion_item
                    })
                    title = bangumi_item.get("title_cn") or bangumi_item.get("title")
                    logger.debug(f"需要更新: {title} (ID: {subject_id})")
        
        # 找出需要删除的记录（仅当enable_delete为True时）
        if self.config.enable_delete:
            for subject_id, notion_item in notion_data.items():
                if subject_id not in bangumi_data:
                    operations["delete"].append(notion_item)
                    notion_props = notion_item.get("properties", {})
                    title = notion_props.get("标题", {}).get("title", [{}])[0].get("text", {}).get("content", "未知标题")
                    logger.debug(f"需要删除: {title} (ID: {subject_id})")
        else:
            logger.info("已禁用删除操作，跳过删除逻辑")
        
        logger.info(f"数据对比完成: 需要添加 {len(operations['add'])} 条记录，更新 {len(operations['update'])} 条记录，删除 {len(operations['delete'])} 条记录")
        return operations
    
    def _need_update(self, bangumi_item: Dict[str, Any], notion_item: Dict[str, Any]) -> bool:
        """判断记录是否需要更新

        Args:
            bangumi_item: Bangumi追番记录
            notion_item: Notion现有记录

        Returns:
            是否需要更新
        """
        notion_props = notion_item.get("properties", {})

        return (self._title_changed(bangumi_item, notion_props) or
                self._score_changed(bangumi_item, notion_props) or
                self._status_changed(bangumi_item, notion_props) or
                self._air_status_changed(bangumi_item, notion_props) or
                self._ep_status_changed(bangumi_item, notion_props) or
                self._total_episodes_changed(bangumi_item, notion_props) or
                self._cover_changed(bangumi_item, notion_item))

    def _title_changed(self, bangumi_item: Dict[str, Any], notion_props: Dict[str, Any]) -> bool:
        """检查标题是否变化"""
        notion_title = notion_props.get("标题", {}).get("title", [{}])[0].get("text", {}).get("content", "")
        if bangumi_item.get("title_cn") != notion_title and bangumi_item.get("title") != notion_title:
            logger.debug(f"标题变更: Bangumi='{bangumi_item.get('title_cn') or bangumi_item.get('title')}', Notion='{notion_title}'")
            return True
        return False

    def _score_changed(self, bangumi_item: Dict[str, Any], notion_props: Dict[str, Any]) -> bool:
        """检查评分是否变化"""
        notion_score = notion_props.get("评分", {}).get("number", 0)
        if bangumi_item.get("score") != notion_score:
            logger.debug(f"评分变更: Bangumi={bangumi_item.get('score')}, Notion={notion_score}")
            return True
        return False

    def _status_changed(self, bangumi_item: Dict[str, Any], notion_props: Dict[str, Any]) -> bool:
        """检查观看状态是否变化"""
        notion_status = notion_props.get("观看状态", {}).get("select", {}).get("name", "")
        mapped_status = NotionConstants.WATCHING_STATUS_MAP.get(bangumi_item.get("status"), "未知")
        if mapped_status != notion_status:
            logger.debug(f"观看状态变更: Bangumi='{mapped_status}', Notion='{notion_status}'")
            return True
        return False

    def _air_status_changed(self, bangumi_item: Dict[str, Any], notion_props: Dict[str, Any]) -> bool:
        """检查播出状态是否变化"""
        notion_air_status = notion_props.get("播出状态", {}).get("select", {}).get("name", "")
        mapped_air_status = NotionConstants.AIR_STATUS_MAP.get(bangumi_item.get("air_status"), "未知")
        if mapped_air_status != notion_air_status:
            logger.debug(f"播出状态变更: Bangumi='{mapped_air_status}', Notion='{notion_air_status}'")
            return True
        return False

    def _ep_status_changed(self, bangumi_item: Dict[str, Any], notion_props: Dict[str, Any]) -> bool:
        """检查已观看集数是否变化"""
        notion_ep_status = notion_props.get("已观看集数", {}).get("number", 0)
        if bangumi_item.get("ep_status") != notion_ep_status:
            logger.debug(f"已观看集数变更: Bangumi={bangumi_item.get('ep_status')}, Notion={notion_ep_status}")
            return True
        return False

    def _total_episodes_changed(self, bangumi_item: Dict[str, Any], notion_props: Dict[str, Any]) -> bool:
        """检查总集数是否变化"""
        notion_total_episodes = notion_props.get("总集数", {}).get("number", 0)
        if bangumi_item.get("total_episodes") != notion_total_episodes:
            logger.debug(f"总集数变更: Bangumi={bangumi_item.get('total_episodes')}, Notion={notion_total_episodes}")
            return True
        return False

    def _cover_changed(self, bangumi_item: Dict[str, Any], notion_item: Dict[str, Any]) -> bool:
        """检查封面是否变化"""
        notion_cover = notion_item.get("cover", {}).get("external", {}).get("url", "")
        if bangumi_item.get("cover") != notion_cover:
            logger.debug(f"封面变更: Bangumi='{bangumi_item.get('cover')}', Notion='{notion_cover}'")
            return True
        return False
    
    def execute_sync(self, operations: Dict[str, List[Any]]) -> None:
        """执行同步操作

        Args:
            operations: 操作列表
        """
        add_items = operations.get("add", [])
        update_items = operations.get("update", [])
        delete_items = operations.get("delete", [])

        total_operations = len(add_items) + len(update_items) + len(delete_items)
        logger.info(f"开始执行同步操作，共 {total_operations} 项任务")

        self._execute_add_operations(add_items, total_operations)
        self._execute_update_operations(update_items, add_items, total_operations)
        self._execute_delete_operations(delete_items, add_items, update_items, total_operations)

        logger.info(f"同步操作完成，共执行 {total_operations} 项任务")

    def _execute_add_operations(self, add_items: List[Dict[str, Any]], total_operations: int) -> None:
        """执行添加操作"""
        for i, bangumi_item in enumerate(add_items, 1):
            title = bangumi_item.get("title_cn") or bangumi_item.get("title")
            logger.info(f"[{i}/{total_operations}] 添加记录: {title}")
            page_data = self.map_bangumi_to_notion(bangumi_item)
            self.notion_client.create_page(page_data)

    def _execute_update_operations(self, update_items: List[Dict[str, Any]],
                                 add_items: List[Dict[str, Any]], total_operations: int) -> None:
        """执行更新操作"""
        for i, item in enumerate(update_items, len(add_items) + 1):
            bangumi_item = item["bangumi_item"]
            notion_item = item["notion_item"]
            title = bangumi_item.get("title_cn") or bangumi_item.get("title")
            logger.info(f"[{i}/{total_operations}] 更新记录: {title}")
            page_data = self.map_bangumi_to_notion(bangumi_item)
            self.notion_client.update_page(notion_item.get("id"), page_data)

    def _execute_delete_operations(self, delete_items: List[Dict[str, Any]],
                                  add_items: List[Dict[str, Any]],
                                  update_items: List[Dict[str, Any]], total_operations: int) -> None:
        """执行删除操作"""
        for i, notion_item in enumerate(delete_items, len(add_items) + len(update_items) + 1):
            notion_props = notion_item.get("properties", {})
            title = notion_props.get("标题", {}).get("title", [{}])[0].get("text", {}).get("content", "未知标题")
            logger.info(f"[{i}/{total_operations}] 删除记录: {title}")
            self.notion_client.update_page(notion_item.get("id"), {"archived": True})
    
    def map_bangumi_to_notion(self, bangumi_item: Dict[str, Any]) -> Dict[str, Any]:
        """将Bangumi数据映射为Notion格式

        Args:
            bangumi_item: Bangumi追番记录

        Returns:
            Notion页面数据
        """
        # 使用中文标题，如果没有则使用日文标题
        title = bangumi_item.get("title_cn") or bangumi_item.get("title")
        
        # 构建Notion页面数据
        page_data = {
            "cover": {
                "external": {
                    "url": bangumi_item.get("cover", "")
                }
            } if bangumi_item.get("cover") else None,
            "properties": {
                "标题": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "评分": {
                    "number": bangumi_item.get("score", 0)
                },
                "观看状态": {
                    "select": {
                        "name": NotionConstants.WATCHING_STATUS_MAP.get(bangumi_item.get("status"), "未知")
                    }
                },
                "播出状态": {
                    "select": {
                        "name": NotionConstants.AIR_STATUS_MAP.get(bangumi_item.get("air_status"), "未知")
                    }
                },
                "已观看集数": {
                    "number": bangumi_item.get("ep_status", 0)
                },
                "总集数": {
                    "number": bangumi_item.get("total_episodes", 0)
                },
                "Bangumi链接": {
                    "url": bangumi_item.get("bangumi_url", "")
                },
                "最后更新时间": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }
        }
        
        # 添加开播日期
        if bangumi_item.get("air_date"):
            page_data["properties"]["开播日期"] = {
                "date": {
                    "start": bangumi_item.get("air_date")
                }
            }
        
        # 添加完结日期
        if bangumi_item.get("end_date"):
            page_data["properties"]["完结日期"] = {
                "date": {
                    "start": bangumi_item.get("end_date")
                }
            }
        
        return page_data
    
    def _log_operations(self, operations: Dict[str, List[Any]]) -> None:
        """记录操作日志

        Args:
            operations: 操作列表
        """
        logger.info("\n=== 模拟运行操作结果 ===")
        
        # 日志添加操作
        logger.info(f"\n需要添加 {len(operations.get('add', []))} 条记录:")
        for bangumi_item in operations.get("add", []):
            title = bangumi_item.get("title_cn") or bangumi_item.get("title")
            logger.info(f"  - {title}")
        
        # 日志更新操作
        logger.info(f"\n需要更新 {len(operations.get('update', []))} 条记录:")
        for item in operations.get("update", []):
            bangumi_item = item["bangumi_item"]
            title = bangumi_item.get("title_cn") or bangumi_item.get("title")
            logger.info(f"  - {title}")
        
        # 日志删除操作
        logger.info(f"\n需要删除 {len(operations.get('delete', []))} 条记录:")
        for notion_item in operations.get("delete", []):
            notion_props = notion_item.get("properties", {})
            title = notion_props.get("标题", {}).get("title", [{}])[0].get("text", {}).get("content", "未知标题")
            logger.info(f"  - {title}")
        
        logger.info("\n=== 模拟运行结束 ===")
