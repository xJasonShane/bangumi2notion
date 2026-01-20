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

## 目录

- [功能特性](#-功能特性)
- [环境要求](#-环境要求)
- [快速开始](#-快速开始)
- [详细配置](#-详细配置)
- [核心功能详解](#-核心功能详解)
- [使用示例](#-使用示例)
- [故障排除](#-故障排除)
- [GitHub Actions 配置](#-github-actions-配置)
- [项目结构](#-项目结构)
- [许可证](#-许可证)
- [联系方式](#-联系方式)

## ✨ 功能特性

- **自动同步** - 从 Bangumi API 获取追番数据，自动同步至 Notion 数据库
- **画廊展示** - 使用番剧海报作为 Notion 画廊封面，美观直观
- **智能更新** - 支持首次全量同步和后续增量更新，仅更新变化的数据
- **定时运行** - 通过 GitHub Actions 实现每日自动同步
- **状态筛选** - 可按观看状态（想看/在看/看过/搁置/抛弃）筛选要同步的记录
- **安全可控** - 可配置是否允许删除 Notion 中不存在的记录
- **完善日志** - 详细的日志记录和错误处理机制
- **自动重试** - API 请求失败时自动重试，提高成功率
- **统一架构** - 采用模块化设计，代码结构清晰，易于维护

## � 环境要求

### 系统要求

- **操作系统**: Windows / macOS / Linux
- **Python 版本**: Python 3.10 或更高版本

### 依赖库

项目依赖以下 Python 库（详见 [requirements.txt](requirements.txt)）：

- `requests` - HTTP 请求库，用于调用 Bangumi API
- `python-dotenv` - 环境变量管理，用于加载 .env 配置文件
- `notion-client` - Notion 官方 Python SDK

### 外部服务

- **Bangumi 账号** - 需要有效的 Bangumi 用户名
- **Notion 集成** - 需要创建 Notion 集成并获取 API Token
- **Notion 数据库** - 需要创建 Notion 数据库并配置相应属性

## �🚀 快速开始

### 1. 准备工作

#### Notion 配置

1. **创建 Notion 集成**
   - 访问 [Notion Integrations](https://www.notion.so/my-integrations)
   - 点击 "New integration" 创建新集成
   - 填写集成名称（如 "bangumi2notion"）
   - 选择关联的工作空间
   - 点击 "Submit" 创建集成
   - 复制生成的 **Internal Integration Token**（即 Notion API Key）

2. **创建 Notion 数据库**
   - 在 Notion 中创建一个新的数据库
   - 选择 **画廊视图**（Gallery View）
   - 添加以下属性（属性名称需完全一致）：

| 属性名称 | 类型 | 说明 |
|---------|------|------|
| 标题 | Title | 番剧标题 |
| 评分 | Number | 番剧评分（1-10） |
| 观看状态 | Select | 选项：想看、在看、看过、搁置、抛弃 |
| 播出状态 | Select | 选项：连载中、已完结、未播出 |
| 开播日期 | Date | 番剧开播日期 |
| 完结日期 | Date | 番剧完结日期（可选） |
| 总集数 | Number | 番剧总集数 |
| 已观看集数 | Number | 用户已观看的集数 |
| Bangumi 链接 | URL | 番剧在 Bangumi 的详情页链接 |
| 最后更新时间 | Date | 记录最后更新时间 |

3. **授权集成访问数据库**
   - 打开创建的数据库页面
   - 点击数据库右上角的 **Share**
   - 在弹出窗口中点击 **Add people, emails, groups...**
   - 搜索并选择你创建的集成名称
   - 点击 **Confirm** 完成授权

4. **获取数据库 ID**
   - 打开数据库页面
   - 复制 URL 中 `https://www.notion.so/` 后的字符串
   - 示例：URL 为 `https://www.notion.so/workspace/a1b2c3d4e5f6g7h8i9j0`，则数据库 ID 为 `a1b2c3d4e5f6g7h8i9j0`

#### Bangumi 配置

- 准备你的 Bangumi 用户名（即 Bangumi.tv 的用户名）

### 2. 安装步骤

```bash
# 克隆仓库
git clone https://github.com/your-username/bangumi2notion.git
cd bangumi2notion

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

#### 方式一：使用 .env 文件（推荐用于本地开发）

1. 在项目根目录创建 `.env` 文件
2. 复制以下内容并根据实际情况填写：

```env
# Bangumi 配置
BANGUMI_USERNAME=your_bangumi_username

# Notion 配置
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# 可选配置
ENABLE_DELETE=true
SYNC_STATUS=all
LOG_LEVEL=INFO
```

#### 方式二：使用环境变量（推荐用于 GitHub Actions）

在运行前设置环境变量：

```bash
# Windows (PowerShell)
$env:BANGUMI_USERNAME="your_bangumi_username"
$env:NOTION_TOKEN="your_notion_integration_token"
$env:NOTION_DATABASE_ID="your_notion_database_id"

# Windows (CMD)
set BANGUMI_USERNAME=your_bangumi_username
set NOTION_TOKEN=your_notion_integration_token
set NOTION_DATABASE_ID=your_notion_database_id

# Linux/macOS
export BANGUMI_USERNAME=your_bangumi_username
export NOTION_TOKEN=your_notion_integration_token
export NOTION_DATABASE_ID=your_notion_database_id
```

### 4. 运行程序

```bash
# 测试运行（不会实际修改数据库）
python bangumi2notion.py --dry-run

# 正式同步
python bangumi2notion.py

# 查看帮助信息
python bangumi2notion.py --help
```

### 5. GitHub Actions 自动同步（可选）

1. **Fork 本仓库**到你的 GitHub 账号
2. 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `BANGUMI_USERNAME` | Bangumi 用户名 | `my_username` |
| `NOTION_TOKEN` | Notion 集成密钥 | `secret_xxx...` |
| `NOTION_DATABASE_ID` | Notion 数据库 ID | `a1b2c3d4e5f6g7h8i9j0` |

4. 进入 **Actions** 标签页，启用工作流
5. 工作流将在每日 **UTC 0 点**自动运行，也可手动触发

## 📋 详细配置

### 环境变量说明

| 变量名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `BANGUMI_USERNAME` | 字符串 | ✅ | - | 你的 Bangumi 用户名 |
| `NOTION_TOKEN` | 字符串 | ✅ | - | Notion 集成密钥（Internal Integration Token） |
| `NOTION_DATABASE_ID` | 字符串 | ✅ | - | 目标 Notion 数据库 ID |
| `ENABLE_DELETE` | 布尔值 | ❌ | `true` | 是否允许删除 Notion 中不存在的番剧记录 |
| `SYNC_STATUS` | 字符串 | ❌ | `all` | 筛选要同步的观看状态，可选值：`all`、`wish`、`watching`、`watched`、`on_hold`、`dropped` |
| `LOG_LEVEL` | 字符串 | ❌ | `INFO` | 日志级别，可选值：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |

### 命令行参数

```bash
python bangumi2notion.py [选项]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--dry-run` | 标志 | `False` | 模拟运行，不实际修改 Notion 数据库 |
| `--log-level` | 字符串 | `INFO` | 设置日志级别，覆盖环境变量中的 `LOG_LEVEL` |
| `--help` | 标志 | - | 显示帮助信息 |

##  核心功能详解

### 数据同步流程

系统采用增量同步机制，流程如下：

1. **获取 Bangumi 数据**
   - 通过 Bangumi API 获取用户追番列表
   - 支持分页获取，自动处理大量数据
   - 自动重试失败的请求（最多 3 次）

2. **解析数据**
   - 提取番剧的核心信息：标题、封面、评分、状态等
   - 映射 Bangumi 状态到 Notion 格式
   - 处理图片 URL（自动补充协议头）

3. **获取 Notion 现有数据**
   - 查询目标数据库中的所有记录
   - 从 Bangumi 链接中提取 subject_id 作为唯一标识

4. **数据对比**
   - 比较 Bangumi 数据与 Notion 数据
   - 识别需要新增、更新或删除的记录
   - 智能判断字段变化，避免不必要的更新

5. **执行同步**
   - 批量执行新增、更新、删除操作
   - 显示实时进度信息
   - 支持模拟运行模式（dry-run）

6. **生成报告**
   - 输出同步结果统计
   - 记录操作日志
   - 显示新增、更新、删除的记录数量

### 状态映射

#### 观看状态映射

| Bangumi 状态码 | Bangumi 状态值 | Notion 状态 |
|--------------|---------------|------------|
| 1 | `wish` | 想看 |
| 2 | `watching` | 在看 |
| 3 | `watched` | 看过 |
| 4 | `on_hold` | 搁置 |
| 5 | `dropped` | 抛弃 |

#### 播出状态映射

| Bangumi 状态码 | Bangumi 状态值 | Notion 状态 |
|--------------|---------------|------------|
| 1 | `watching` | 连载中 |
| 2 | `finished` | 已完结 |
| 3 | `not_aired` | 未播出 |

### 同步字段详解

| Bangumi 字段 | Notion 属性类型 | 说明 | 示例 |
|--------------|----------------|------|------|
| 标题 | Title | 番剧标题（优先显示中文，若无则显示日文） | "进击的巨人" |
| 封面图片 | Cover | 番剧海报，作为画廊封面 | `https://...` |
| 评分 | Number | 番剧评分，1-10 分 | 8.5 |
| 观看状态 | Select | 用户的观看状态 | "在看" |
| 播出状态 | Select | 番剧的播出状态 | "连载中" |
| 开播日期 | Date | 番剧开播日期 | 2023-04-01 |
| 完结日期 | Date | 番剧完结日期（若未完结则为空） | 2023-06-30 |
| 总集数 | Number | 番剧总集数 | 25 |
| 已观看集数 | Number | 用户已观看的集数 | 12 |
| Bangumi 链接 | URL | 番剧在 Bangumi 的详情页链接 | `https://bangumi.tv/subject/xxx` |
| 最后更新时间 | Date | 记录最后更新时间 | 2024-01-15T10:30:00Z |

## 📚 使用示例

### 基本使用

```bash
# 基本同步（使用 .env 文件中的配置）
python bangumi2notion.py

# 查看帮助信息
python bangumi2notion.py --help
```

### 高级使用

#### 1. 仅同步特定状态的番剧

```bash
# 仅同步「在看」状态的番剧
export SYNC_STATUS=watching
python bangumi2notion.py

# 仅同步「想看」状态的番剧
export SYNC_STATUS=wish
python bangumi2notion.py

# 同步所有状态的番剧（默认）
export SYNC_STATUS=all
python bangumi2notion.py
```

#### 2. 禁用删除功能

```bash
# 禁用删除操作，仅新增和更新记录
export ENABLE_DELETE=false
python bangumi2notion.py
```

#### 3. 调整日志级别

```bash
# 开启调试日志，查看详细执行过程
python bangumi2notion.py --log-level DEBUG

# 仅显示错误信息
python bangumi2notion.py --log-level ERROR

# 使用环境变量设置日志级别
export LOG_LEVEL=DEBUG
python bangumi2notion.py
```

#### 4. 模拟运行

```bash
# 模拟运行，不实际修改数据库，用于预览同步结果
python bangumi2notion.py --dry-run
```

#### 5. 组合使用多个参数

```bash
# 仅同步「在看」状态的番剧，开启调试日志，模拟运行
export SYNC_STATUS=watching
python bangumi2notion.py --log-level DEBUG --dry-run
```

### 常见场景

#### 场景 1：首次同步

```bash
# 1. 配置 .env 文件
# 2. 先进行模拟运行，检查配置是否正确
python bangumi2notion.py --dry-run

# 3. 确认无误后，执行正式同步
python bangumi2notion.py
```

#### 场景 2：定期自动同步

```bash
# 使用 GitHub Actions 设置每日自动同步
# 或使用系统定时任务（如 cron）
# 每天凌晨 2 点执行
0 2 * * * python /path/to/bangumi2notion.py
```

#### 场景 3：仅更新特定状态的番剧

```bash
# 只同步「在看」和「看过」的番剧
export SYNC_STATUS=watching
python bangumi2notion.py
export SYNC_STATUS=watched
python bangumi2notion.py
```

#### 场景 4：排查同步问题

```bash
# 开启调试日志，查看详细的 API 请求和响应
python bangumi2notion.py --log-level DEBUG

# 使用模拟运行，检查哪些记录会被修改
python bangumi2notion.py --dry-run
```

## � 故障排除

### 常见问题

#### 1. 配置错误：缺少必要的环境变量

**错误信息**：
```
ConfigError: 缺少必要的环境变量: BANGUMI_USERNAME, NOTION_TOKEN
```

**解决方案**：
- 检查 `.env` 文件是否存在
- 确认环境变量名称拼写正确
- 确保 GitHub Actions Secrets 已正确配置

#### 2. Notion API 错误：权限不足

**错误信息**：
```
NotionAPIError: Notion API请求失败: 403 Forbidden
```

**解决方案**：
- 确认已将集成添加到数据库的共享列表中
- 检查集成 Token 是否有效
- 确认数据库 ID 是否正确

#### 3. Bangumi API 错误：用户不存在

**错误信息**：
```
BangumiAPIError: Bangumi API请求失败: 404 Not Found
```

**解决方案**：
- 确认 Bangumi 用户名拼写正确
- 检查用户名是否为空或包含特殊字符
- 尝试在浏览器中访问用户主页验证

#### 4. 数据库属性不匹配

**错误信息**：
```
NotionAPIError: 创建Notion页面失败
```

**解决方案**：
- 检查 Notion 数据库属性名称是否与文档要求完全一致
- 确认属性类型是否正确（Title、Number、Select、Date、URL）
- 检查 Select 选项是否包含所有状态值

#### 5. 网络连接问题

**错误信息**：
```
BangumiAPIError: Bangumi API请求失败: ConnectionError
```

**解决方案**：
- 检查网络连接是否正常
- 确认防火墙或代理设置
- 程序会自动重试 3 次，如仍失败请检查网络环境

#### 6. 同步结果不符合预期

**问题**：Notion 中没有显示某些番剧

**解决方案**：
- 检查 `SYNC_STATUS` 配置，确认是否过滤了该状态的番剧
- 使用 `--dry-run` 参数预览同步结果
- 开启 `DEBUG` 日志级别查看详细执行过程

### 调试技巧

#### 开启详细日志

```bash
# 查看所有 API 请求和响应
python bangumi2notion.py --log-level DEBUG
```

#### 使用模拟运行

```bash
# 预览将要执行的操作，不实际修改数据
python bangumi2notion.py --dry-run
```

#### 检查配置

```bash
# 在 Python 中验证配置
python -c "from config import Config; print(Config())"
```

### 获取帮助

如遇到其他问题：
1. 查看日志输出，定位错误信息
2. 参考 [故障排除](#-故障排除) 部分
3. 提交 [Issue](https://github.com/xJasonShane/bangumi2notion/issues) 并附上：
   - 错误信息
   - 日志输出（使用 `--log-level DEBUG`）
   - 配置信息（隐藏敏感信息）
   - 操作系统版本

## �🔄 GitHub Actions 配置

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

    # 每周一凌晨 2 点执行
    # - cron: '0 2 * * 1'

  workflow_dispatch:  # 支持手动触发
```

### Cron 表达式说明

| 字段 | 允许值 | 说明 |
|------|---------|------|
| 分钟 | 0-59 | 每小时的第几分钟 |
| 小时 | 0-23 | 每天的第几小时 |
| 日期 | 1-31 | 每月的第几天 |
| 月份 | 1-12 | 每年的第几月 |
| 星期 | 0-6 | 每周的第几天（0=周日） |

### 查看运行日志

1. 进入 GitHub 仓库 → **Actions** 标签页
2. 点击最新的 workflow 运行记录
3. 展开 **Run sync** 步骤
4. 查看详细的输出日志

### 手动触发同步

1. 进入 GitHub 仓库 → **Actions** 标签页
2. 选择左侧的 **Bangumi Sync** workflow
3. 点击右侧的 **Run workflow** 按钮
4. 选择要使用的分支（默认为 `main`）
5. 点击 **Run workflow** 确认执行

## 📁 项目结构

```
bangumi2notion/
├── bangumi2notion.py      # 主程序入口
├── bangumi_client.py      # Bangumi API 客户端
├── notion_service.py      # Notion API 服务
├── sync_manager.py        # 同步逻辑核心
├── config.py              # 配置管理
├── constants.py           # 统一常量管理
├── exceptions.py          # 统一异常管理
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例文件
├── .gitignore             # Git 忽略规则
├── .github/
│   └── workflows/
│       └── sync.yml       # GitHub Actions 配置
├── LICENSE                # 许可证文件
└── README.md              # 项目说明文档
```

### 模块说明

- **bangumi2notion.py** - 程序入口，负责参数解析、日志配置和流程编排
- **bangumi_client.py** - Bangumi API 客户端，封装 API 请求、重试机制和数据解析
- **notion_service.py** - Notion API 服务，封装数据库查询、页面创建和更新操作
- **sync_manager.py** - 同步管理器，负责数据对比、差异计算和同步执行
- **config.py** - 配置管理，加载和验证环境变量
- **constants.py** - 常量管理，统一管理 API 配置和状态映射
- **exceptions.py** - 异常管理，定义自定义异常类

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 📞 联系方式

- 如有问题或建议，欢迎提交 [Issue](https://github.com/xJasonShane/bangumi2notion/issues)
- 欢迎加入讨论，分享使用经验和建议
- 查看项目主页获取最新信息：[https://github.com/xJasonShane/bangumi2notion](https://github.com/xJasonShane/bangumi2notion)

---

<div align="center">
  <p>如果这个项目对你有帮助，请给个 ⭐ 支持一下吧！</p>
</div>
