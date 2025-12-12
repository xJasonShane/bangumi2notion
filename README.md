# bangumi2notion

<div align="center">
  <p>
    <strong>将 Bangumi 追番记录自动同步到 Notion 数据库的工具</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
    <img src="https://img.shields.io/badge/GitHub%20Actions-Automatic%20Update-yellow.svg" alt="GitHub Actions">
  </p>
</div>

## ✨ 功能特性

- 📥 **自动同步**：从 Bangumi API 获取追番数据，自动同步至 Notion 数据库
- 🖼️ **画廊展示**：使用番剧海报作为 Notion 画廊封面，美观直观
- 🔄 **智能更新**：支持首次全量同步和后续增量更新，只更新变化的数据
- ⏰ **定时运行**：通过 GitHub Actions 实现每日自动同步
- 🎯 **状态筛选**：可按观看状态（想看/在看/看过/搁置/抛弃）筛选要同步的记录
- 🗑️ **安全可控**：可配置是否允许删除 Notion 中不存在的记录
- 📊 **完善日志**：详细的日志记录和错误处理机制
- 🔁 **自动重试**：API 请求失败时自动重试，提高成功率

## 🚀 快速开始

### 1. 准备工作

**Notion 配置**
1. 访问 [Notion Integrations](https://www.notion.so/my-integrations) 创建一个新集成
2. 复制生成的 **Internal Integration Token**（Notion API Key）
3. 在 Notion 中创建一个新的数据库，选择 **画廊视图**
4. 点击数据库右上角的 **Share**，邀请你的集成访问该数据库
5. 复制数据库 ID：打开数据库页面，URL 中 `https://www.notion.so/` 后的字符串即为数据库 ID

**Bangumi 配置**
- 准备你的 Bangumi 用户名

### 2. 本地运行

```bash
# 克隆仓库
git clone https://github.com/your-username/bangumi2notion.git
cd bangumi2notion

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置信息
# 使用文本编辑器打开 .env 文件，替换相应的值

# 测试运行（不会实际修改数据库）
python bangumi2notion.py --dry-run

# 正式同步
python bangumi2notion.py
```

### 3. GitHub Actions 自动同步

1. **Fork 本仓库**到你的 GitHub 账号
2. 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
3. 添加以下 **Repository Secrets**：
   - `BANGUMI_USERNAME`：你的 Bangumi 用户名
   - `NOTION_TOKEN`：Notion 集成密钥
   - `NOTION_DATABASE_ID`：Notion 数据库 ID
4. 进入 **Actions** 标签页，启用工作流
5. 工作流将在每日 **UTC 0 点**自动运行，也可手动触发

## 📋 详细配置

### 环境变量

| 变量名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `BANGUMI_USERNAME` | 字符串 | ✅ | - | 你的 Bangumi 用户名 |
| `NOTION_TOKEN` | 字符串 | ✅ | - | Notion 集成密钥 |
| `NOTION_DATABASE_ID` | 字符串 | ✅ | - | 目标 Notion 数据库 ID |
| `ENABLE_DELETE` | 布尔值 | ❌ | `true` | 是否允许删除 Notion 中不存在的番剧记录 |
| `SYNC_STATUS` | 字符串 | ❌ | `all` | 筛选要同步的观看状态，可选值：`all`、`wish`、`watching`、`watched`、`on_hold`、`dropped` |
| `LOG_LEVEL` | 字符串 | ❌ | `INFO` | 日志级别，可选值：`DEBUG`、`INFO`、`WARNING`、`ERROR` |

### 命令行参数

```bash
python bangumi2notion.py [选项]
```

| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--dry-run` | 标志 | `False` | 模拟运行，不实际修改数据库 |
| `--log-level` | 字符串 | `INFO` | 设置日志级别 |
| `--help` | 标志 | - | 显示帮助信息 |

## 📁 项目结构

```
bangumi2notion/
├── bangumi2notion.py      # 主程序入口
├── bangumi_client.py      # Bangumi API 客户端
├── notion_service.py      # Notion API 服务
├── sync_manager.py        # 同步逻辑核心
├── config.py              # 配置管理
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例文件
├── .gitignore             # Git 忽略规则
├── .github/
│   └── workflows/
│       └── sync.yml       # GitHub Actions 配置
├── LICENSE                # 许可证文件
└── README.md              # 项目说明文档
```

## 🔧 核心功能详解

### 数据同步流程

1. **获取 Bangumi 数据**：通过 Bangumi API 获取用户追番列表
2. **解析数据**：提取番剧的核心信息，如标题、封面、评分、状态等
3. **获取 Notion 现有数据**：查询目标数据库中的现有记录
4. **数据对比**：比较 Bangumi 数据与 Notion 数据，确定需要新增、更新或删除的记录
5. **执行同步**：根据对比结果执行相应的操作
6. **生成报告**：输出同步结果统计

### 状态映射

| Bangumi 状态 | Notion 状态 |
|--------------|------------|
| `wish`       | 想看        |
| `watching`   | 在看        |
| `watched`    | 看过        |
| `on_hold`    | 搁置        |
| `dropped`    | 抛弃        |

| Bangumi 播出状态 | Notion 播出状态 |
|------------------|----------------|
| 连载中           | 连载中         |
| 已完结           | 已完结         |
| 未播出           | 未播出         |

### 同步字段

| Bangumi 字段 | Notion 属性类型 | 描述 |
|--------------|----------------|------|
| 标题         | Title          | 番剧标题（优先显示中文，若无则显示日文） |
| 封面图片     | Cover          | 番剧海报，作为画廊封面 |
| 评分         | Number         | 番剧评分，1-10分 |
| 观看状态     | Select         | 用户的观看状态 |
| 播出状态     | Select         | 番剧的播出状态 |
| 开播日期     | Date           | 番剧开播日期 |
| 完结日期     | Date           | 番剧完结日期（若未完结则为空） |
| 总集数       | Number         | 番剧总集数 |
| 已观看集数   | Number         | 用户已观看的集数 |
| Bangumi 链接 | URL            | 番剧在 Bangumi 的详情页链接 |
| 最后更新时间 | Date           | 记录最后更新时间 |

## 📚 使用示例

### 基本使用

```bash
# 基本同步
python bangumi2notion.py

# 查看帮助信息
python bangumi2notion.py --help
```

### 高级使用

```bash
# 仅同步「在看」状态的番剧
export SYNC_STATUS=watching
python bangumi2notion.py

# 禁用删除功能
export ENABLE_DELETE=false
python bangumi2notion.py

# 开启调试日志
python bangumi2notion.py --log-level DEBUG

# 模拟运行，不实际修改数据库
python bangumi2notion.py --dry-run
```

## 🔄 GitHub Actions 配置

### 自定义同步时间

编辑 `.github/workflows/sync.yml` 文件中的 `cron` 表达式，自定义同步时间：

```yaml
on:
  schedule:
    # 每日 UTC 时间 0 点执行
    - cron: '0 0 * * *'
    # 每日北京时间 0 点执行（UTC+8）
    # - cron: '0 16 * * *'
    # 每 6 小时执行一次
    # - cron: '0 */6 * * *'
  workflow_dispatch:  # 支持手动触发
```

### 查看运行日志

1. 进入 GitHub 仓库 → **Actions** 标签页
2. 点击最新的 workflow 运行记录
3. 查看 **Run sync** 步骤的输出日志

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 📞 联系方式

- 如有问题或建议，欢迎提交 [Issue](https://github.com/xJasonShane/bangumi2notion/issues)
- 欢迎加入讨论，分享使用经验和建议

---

<div align="center">
  <p>如果这个项目对你有帮助，请给个 ⭐ 支持一下吧！</p>
</div>