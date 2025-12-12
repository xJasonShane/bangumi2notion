import argparse
import logging
import sys

from config import Config, ConfigError
from bangumi_client import BangumiClient, BangumiAPIError
from notion_service import NotionService, NotionAPIError
from sync_manager import SyncManager, SyncError


def setup_logging(log_level):
    """配置日志
    
    Args:
        log_level: 日志级别
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments():
    """解析命令行参数
    
    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(description='将Bangumi追番记录同步到Notion数据库')
    parser.add_argument('--log-level', type=str, default='INFO', 
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='日志级别')
    parser.add_argument('--dry-run', action='store_true', 
                      help='模拟运行，不实际修改Notion数据库')
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 配置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("启动bangumi2notion同步工具")
    
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
        logger.info(f"同步结果统计:")
        logger.info(f"  Bangumi追番总数: {result['total_bangumi_items']}")
        logger.info(f"  Notion现有记录: {result['total_notion_items']}")
        logger.info(f"  新增记录数: {result['add_count']}")
        logger.info(f"  更新记录数: {result['update_count']}")
        logger.info(f"  删除记录数: {result['delete_count']}")
        
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
