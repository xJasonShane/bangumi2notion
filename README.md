# bangumi2notion

一个将Bangumi网站的追番记录自动同步到Notion数据库的工具，支持通过GitHub Actions实现每日自动更新。

## 功能特性

- ✅ 从Bangumi API获取用户追番记录
- ✅ 将追番记录同步到Notion数据库
- ✅ 使用Bangumi番剧海报作为Notion画廊视图封面
- ✅ 支持首次全量同步和后续增量更新
- ✅ 实现API请求失败重试机制
- ✅ 支持模拟运行，不实际修改数据库
- ✅ 通过GitHub Actions实现每日自动同步
- ✅ 支持按观看状态过滤同步记录
- ✅ 可配置是否允许删除记录
- ✅ 完善的日志记录和错误处理

## 安装

### 环境要求

- Python 3.10+
- Git

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/your-username/bangumi2notion.git
cd bangumi2notion
```

2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

### 环境变量

| 环境变量名               | 类型     | 必填 | 默认值 | 描述                     |
|-------------------------|----------|------|--------|--------------------------|
| BANGUMI_USERNAME        | 字符串   | 是   | 无     | Bangumi用户名           |
| NOTION_TOKEN            | 字符串   | 是   | 无     | Notion API密钥           |
| NOTION_DATABASE_ID      | 字符串   | 是   | 无     | Notion数据库ID           |
| LOG_LEVEL               | 字符串   | 否   | INFO   | 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL） |
| SYNC_INTERVAL           | 整数     | 否   | 86400  | 同步间隔（秒）          |
| ENABLE_DELETE           | 布尔值   | 否   | true   | 是否允许删除记录        |
| SYNC_STATUS             | 字符串   | 否   | all    | 过滤同步记录（all, watching, watched, wish, on_hold, dropped） |

### .env文件（可选）

创建一个 `.env` 文件，将环境变量配置写入其中：

```
# .env 文件内容
BANGUMI_USERNAME=your_bangumi_username
NOTION_TOKEN=secret_your_notion_token
NOTION_DATABASE_ID=your_notion_database_id
LOG_LEVEL=INFO
ENABLE_DELETE=true
SYNC_STATUS=all
```

### 获取Notion配置

1. **获取Notion API密钥**
   - 访问 https://www.notion.so/my-integrations
   - 创建一个新的集成
   - 复制生成的API密钥

2. **获取Notion数据库ID**
   - 在Notion中创建一个新的数据库
   - 点击数据库右上角的 "Share" 按钮
   - 邀请你的集成访问该数据库
   - 复制数据库页面URL中的数据库ID部分
     - URL格式：`https://www.notion.so/xxx/<database_id>?v=xxx`
     - `<database_id>` 即为数据库ID

## 使用方法

### 手动运行

```bash
# 激活虚拟环境
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 基本运行
python bangumi2notion.py

# 模拟运行，不实际修改数据库
python bangumi2notion.py --dry-run

# 设置日志级别
python bangumi2notion.py --log-level DEBUG
```

### 命令行参数

| 参数名       | 类型     | 默认值 | 描述                     |
|-------------|----------|--------|--------------------------|
| --dry-run   | 标志     | False  | 模拟运行，不实际修改数据库 |
| --log-level | 字符串   | INFO   | 设置日志级别             |

## GitHub Actions配置

1. 登录GitHub，进入项目仓库
2. 点击 "Settings" > "Secrets and variables" > "Actions"
3. 添加以下Secrets：
   - `BANGUMI_USERNAME`: Bangumi用户名
   - `NOTION_TOKEN`: Notion API密钥
   - `NOTION_DATABASE_ID`: Notion数据库ID
4. 工作流将在每日UTC 0点自动运行，也可以手动触发

### 自定义同步时间

编辑 `.github/workflows/sync.yml` 文件中的cron表达式，修改同步时间：

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # 每日UTC 0点执行
```

## 开发指南

### 项目结构

```
bangumi2notion/
├── bangumi2notion.py      # 主程序入口
├── bangumi_client.py      # Bangumi API客户端
├── notion_service.py      # Notion API服务
├── sync_manager.py        # 同步管理器
├── config.py              # 配置管理
├── requirements.txt       # 依赖列表
├── .gitignore             # Git忽略规则
├── .github/workflows/sync.yml  # GitHub Actions配置
├── Requirements.md        # 需求文档
├── Design.md              # 设计文档
├── Development.md         # 开发文档
└── README.md              # 项目说明
```

### 开发流程

1. 创建特性分支
2. 实现功能
3. 运行测试
4. 提交代码
5. 创建Pull Request

### 测试

```bash
# 运行模拟测试
python bangumi2notion.py --dry-run
```

## 数据字段映射

| Bangumi字段          | Notion字段          | Notion属性类型 |
|--------------------|--------------------|---------------|
| 标题（中文/日文）     | 标题                | Title         |
| 封面图片URL          | 封面                | Cover         |
| 评分                | 评分                | Number        |
| 观看状态             | 观看状态            | Select        |
| 播出状态             | 播出状态            | Select        |
| 开播日期             | 开播日期            | Date          |
| 完结日期             | 完结日期            | Date          |
| 总集数              | 总集数              | Number        |
| 已观看集数           | 已观看集数          | Number        |
| Bangumi详情页URL     | Bangumi链接         | URL           |
| 更新时间             | 最后更新时间        | Date          |

## 观看状态映射

| Bangumi状态    | Notion状态    |
|---------------|---------------|
| wish          | 想看          |
| watching      | 在看          |
| watched       | 看过          |
| on_hold       | 搁置          |
| dropped       | 抛弃          |

## 播出状态映射

| Bangumi状态    | Notion状态    |
|---------------|---------------|
| watching      | 连载中        |
| finished      | 已完结        |
| not_aired     | 未播出        |

## 致谢

- [Bangumi](https://bangumi.tv/)
- [Notion](https://www.notion.so/)
- [notion-client](https://github.com/ramnes/notion-sdk-py)

## 联系方式

如有问题或建议，欢迎通过GitHub Issues反馈。
