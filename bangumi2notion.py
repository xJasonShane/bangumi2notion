import argparse
import logging
import sys
from typing import Dict, Any

from config import Config
from bangumi_client import BangumiClient
from notion_service import NotionService
from sync_manager import SyncManager
from exceptions import ConfigError, BangumiAPIError, NotionAPIError, SyncError


def setup_logging(log_level: str) -> None:
    """配置日志
    
    Args:
        log_level: 日志级别
    """
    # 创建日志格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    
    # 减少第三方库的日志级别
    for lib in ['requests', 'urllib3', 'notion_client']:
        logging.getLogger(lib).setLevel(logging.WARNING)


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数
    
    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='将Bangumi网站的追番记录自动同步到Notion数据库',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--dry-run', action='store_true', 
                      help='模拟运行，不实际修改Notion数据库')
    
    parser.add_argument('--log-level', type=str, default='INFO', 
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='设置日志级别')
    
    return parser.parse_args()


def main() -> None:
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 配置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("启动bangumi2notion同步工具")
    logger.debug(f"命令行参数: {args}")
    
    try:
        # 加载配置
        config = Config()
        logger.debug(f"加载配置成功: {config}")
        
        # 初始化客户端
        bangumi_client = BangumiClient()
        notion_client = NotionService(config.notion_token, config.notion_database_id)
        
        # 初始化同步管理器
        sync_manager = SyncManager(bangumi_client, notion_client, config)
        
        # 执行同步
        result = sync_manager.sync(dry_run=args.dry_run)
        
        # 输出同步结果
        logger.info("\n=== 同步结果统计 ===")
        logger.info(f"Bangumi追番总数: {result['total_bangumi_items']}")
        logger.info(f"Notion现有记录: {result['total_notion_items']}")
        logger.info(f"新增记录数: {result['add_count']}")
        logger.info(f"更新记录数: {result['update_count']}")
        logger.info(f"删除记录数: {result['delete_count']}")
        logger.info("==================")
        
        logger.info("bangumi2notion同步工具执行完成")
        sys.exit(0)
        
    except ConfigError as e:
        logger.error(f"配置错误: {e}")
        sys.exit(1)
    except BangumiAPIError as e:
        logger.error(f"Bangumi API错误: {e}")
        sys.exit(1)
    except NotionAPIError as e:
        logger.error(f"Notion API错误: {e}")
        sys.exit(1)
    except SyncError as e:
        logger.error(f"同步错误: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生意外错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
