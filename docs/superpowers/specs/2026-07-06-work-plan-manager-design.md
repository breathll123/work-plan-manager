# 工作计划管理系统 · 设计文档

日期:2026-07-06
状态:待用户审阅

## 1. 概述

一个本地单机的 Windows 工作计划管理软件。用户按分类管理工作计划,在日历中查看安排,每条计划可绑定多个文件夹或文件,点击即可跳转到资源管理器。Python 编写,最终打包为单个 .exe 分发,数据随软件目录便携存储。

**开发环境说明**:日常在 macOS 上开发调试(PySide6 跨平台运行),.exe 打包必须在 Windows 上执行(PyInstaller 不支持跨平台打包)。仓库提供 `build.bat` 供 Windows 本机打包,并附 GitHub Actions 配置可选自动打包。

## 2. 需求(已确认的决策)

| 决策点 | 结论 |
|---|---|
| 计划时间形态 | 支持单日与跨天:每条计划有开始日期和结束日期,单日即两者相同;不含具体钟点 |
| 状态跟踪 | 三态:未开始 / 进行中 / 已完成 |
| 分类方式 | 用户自定义平级分类,每个分类一个颜色;计划最多属于一个分类,可无分类 |
| 文件夹绑定 | 每条计划可绑定多个路径(文件夹或文件),点击用资源管理器/系统默认方式打开 |
| 视图 | 日历月视图(默认)+ 列表视图;不做周视图 |
| 提醒 | 仅在软件启动时汇总提示「今日到期」与「已逾期未完成」;不做后台常驻/托盘/开机自启 |
| 数据存放 | 便携模式:`workplan.db` 与 exe 同目录,拷走即用 |
| 技术栈 | PySide6 + SQLite(标准库 sqlite3)+ PyInstaller |

### 非目标(明确不做)

- 周视图、按钟点的时间轴视图
- 关键词搜索
- 重复/周期性计划
- 后台常驻、系统托盘、开机自启、定时弹通知
- 多用户、云同步、网络功能

## 3. 架构

三层架构,单向依赖,服务层与数据层不含任何 GUI 代码:

```
UI 层 (PySide6)          主窗口、月历控件、列表视图、计划编辑对话框
   ↓ 调用
服务层 (纯 Python)        PlanService / CategoryService / ReminderService
   ↓ 调用                 业务规则:日期校验、状态流转、启动提醒汇总
数据层 (sqlite3)          Repository 封装全部 SQL,返回 dataclass 模型
   ↓
SQLite 文件               exe 同目录 workplan.db(WAL 模式)
```

### 项目结构

```
工作计划Windows/
├── app/
│   ├── main.py                 入口:初始化 DB、装配服务、启动主窗口
│   ├── ui/
│   │   ├── main_window.py      主窗口:工具栏、左侧分类栏、视图切换
│   │   ├── calendar_view.py    月历控件(自绘网格与计划条带)
│   │   ├── list_view.py        列表视图(表格 + 筛选条)
│   │   ├── plan_dialog.py      计划新建/编辑对话框
│   │   ├── category_dialog.py  分类管理对话框
│   │   └── reminder_dialog.py  启动提醒汇总对话框
│   ├── services/
│   │   ├── plan_service.py
│   │   ├── category_service.py
│   │   └── reminder_service.py
│   ├── data/
│   │   ├── db.py               连接、建表、WAL、启动备份
│   │   ├── models.py           dataclass:Category / Plan / PlanLink
│   │   └── repositories.py     CategoryRepo / PlanRepo / PlanLinkRepo
│   └── platform_utils.py       打开路径:Windows 用 os.startfile,macOS 用 open
├── tests/                      pytest:服务层 + 数据层
├── build.bat                   Windows 打包脚本(PyInstaller)
├── .github/workflows/build.yml GitHub Actions Windows 自动打包(可选)
├── requirements.txt
└── docs/superpowers/specs/     本文档
```

## 4. 数据模型

SQLite,3 张表:

```sql
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    color       TEXT NOT NULL,              -- 十六进制,如 '#4A90D9'
    sort_order  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE plans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    note        TEXT NOT NULL DEFAULT '',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    start_date  TEXT NOT NULL,              -- ISO 格式 'YYYY-MM-DD'
    end_date    TEXT NOT NULL,              -- 单日计划 start_date = end_date
    status      INTEGER NOT NULL DEFAULT 0, -- 0 未开始 / 1 进行中 / 2 已完成
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    CHECK (end_date >= start_date)
);

CREATE TABLE plan_links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id     INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    path        TEXT NOT NULL,              -- 文件夹或文件的绝对路径
    sort_order  INTEGER NOT NULL DEFAULT 0
);
```

规则:

- 删除分类:该分类下的计划 `category_id` 置 NULL(归入「未分类」),计划不删除
- 删除计划:级联删除其全部 `plan_links`
- 日期一律以 `YYYY-MM-DD` 字符串存储,业务层用 `datetime.date` 处理
- 外键约束开启(`PRAGMA foreign_keys = ON`)

## 5. 界面与交互

### 主窗口布局

```
┌──────────────────────────────────────────────────┐
│ 工具栏: [◀ 上月] 2026年7月 [下月 ▶] [今天]  [月历|列表] [+新建] │
├────────────┬─────────────────────────────────────┤
│ 左侧分类栏  │  月历视图(默认)或列表视图              │
│ ☑ 项目A ●  │                                     │
│ ☑ 日常 ●   │                                     │
│ ☐ 未分类    │                                     │
│ [管理分类]  │                                     │
└────────────┴─────────────────────────────────────┘
```

- 左侧分类栏:复选框筛选(未勾选的分类在两个视图中都隐藏),默认全部勾选(含「未分类」);「管理分类」打开分类管理对话框(增删改名、选颜色、排序)
- 视图切换按钮在工具栏,月份导航仅对月历视图生效
- 工具栏「+新建」:打开新建计划对话框,起止日期预填今天

### 月历视图

- 周一为每周第一天,7 列网格,当月外的日期灰显
- 每格内按行显示当天的计划条:分类色块背景 + 标题文字
- 跨天计划渲染为横跨多格的连续条带;跨周时断行续排
- 已完成:灰色 + 删除线;逾期未完成(end_date < 今天 且 status ≠ 已完成):条带上加红色标记
- 今天的格子高亮边框
- 单格计划过多时显示「+N 更多」,点击展开当日全部
- 交互:单击某天格子 → 弹出该日计划列表小窗(非模态,列出当天全部计划,可点入编辑);双击空白 → 新建当天计划(起止日期预填该天);单击计划条 → 打开编辑对话框

### 计划编辑对话框

字段:标题(必填)、分类下拉(含「未分类」)、开始日期、结束日期(两个日期选择器,校验 end ≥ start)、状态三选、备注多行文本。

绑定路径区:

- 「添加文件夹」/「添加文件」按钮,调系统选择对话框
- 列表逐行显示路径,每行有「打开」和「移除」按钮
- 失效路径(磁盘上已不存在)整行标红并提示「路径不存在」;点「打开」时弹提示而非崩溃

对话框内有「删除计划」按钮(带确认)。

### 列表视图

- 表格列:状态、标题、分类、开始日期、结束日期、绑定路径数
- 顶部筛选条:分类下拉、状态下拉、日期范围;与左侧分类栏筛选叠加生效
- 双击行打开编辑对话框;默认按开始日期升序

### 启动提醒

程序启动后,若存在「今日到期(end_date = 今天,未完成)」或「已逾期(end_date < 今天,未完成)」的计划,弹出汇总对话框,分两组列出;点击条目直接打开该计划的编辑对话框。无匹配则不弹。

### 打开路径

`platform_utils.open_path(path)`:Windows 用 `os.startfile()`;macOS(开发环境)用 `subprocess.run(['open', path])`。路径不存在时返回错误由 UI 提示。

## 6. 错误处理与数据安全

- **失效路径**:显示层标红,打开时友好提示,绝不抛未捕获异常
- **SQLite WAL 模式**:降低写入损坏风险
- **启动自动备份**:每次启动把 `workplan.db` 复制为 `backups/workplan-YYYYMMDD-HHMMSS.db`,只保留最近 5 份,滚动删除
- **目录不可写**:启动时检测 exe 所在目录可写性;不可写则弹窗说明「请将软件放到可写目录(不要放 Program Files)」后退出
- **全局异常兜底**:`sys.excepthook` 捕获未处理异常,写入同目录 `error.log`,弹窗告知用户后尽量不退出
- **数据库升级**:表结构带 `schema_version`(PRAGMA user_version),为将来升级留迁移入口

## 7. 测试策略

- **pytest 覆盖服务层与数据层**(使用临时 SQLite 文件,无 GUI 依赖):
  - 计划增删改查、日期校验(end ≥ start)、跨天计划落在哪些天的计算
  - 删除分类后计划归入未分类;删除计划级联删链接
  - 提醒汇总:今日到期/已逾期的筛选边界(今天、昨天、明天)
  - 备份滚动保留 5 份的逻辑
- **GUI 手动冒烟清单**(打包后在 Windows 上过一遍):
  1. 新建分类并配色 → 月历上颜色正确
  2. 新建单日计划、跨天计划 → 月历显示正确,跨周条带断行正常
  3. 绑定文件夹和文件 → 点击「打开」跳转正确
  4. 移走绑定的文件夹 → 标红提示
  5. 标记完成 → 灰色划线;制造逾期 → 红色标记 + 启动弹提醒
  6. 列表视图筛选、双击编辑
  7. 关闭软件拷贝整个目录到别处 → 数据完整随行

## 8. 打包与分发

- PyInstaller `--onefile --windowed --icon=app.ico`,产物为单个 `工作计划.exe`
- `build.bat`:Windows 上安装依赖并执行打包,双击即可
- `.github/workflows/build.yml`:推送 tag 时在 windows-latest 上打包并上传 artifact(可选使用)
- 首次启动 2-4 秒解压属 onefile 正常现象
- 依赖锁定在 `requirements.txt`(PySide6、pyinstaller、pytest)

## 9. 里程碑划分(供实现计划参考)

1. 数据层 + 服务层 + 全部 pytest(无 GUI,可在 Mac 上完成并验证)
2. 主窗口骨架 + 分类管理 + 列表视图
3. 月历视图(含跨天条带渲染)
4. 计划编辑对话框 + 路径绑定与跳转
5. 启动提醒 + 备份 + 异常兜底
6. Windows 打包与冒烟测试
