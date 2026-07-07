# 工作计划

本地便携版工作计划管理软件:分类管理、月历/列表视图、文件夹绑定一键跳转、
启动待办提醒、浅色/深色主题。数据存在软件同目录的 `data/workplan.db`,
整个软件文件夹拷走即可迁移。

## 开发(macOS / Windows / Linux)

```bash
conda create -n workplan python=3.11
conda activate workplan
pip install -r requirements.txt
python -m app.main
python -m pytest -q
```

## 打包成 Windows exe

PyInstaller 不支持跨平台打包,必须在 Windows 上执行(二选一):

1. 本机打包:把仓库拷到 Windows 电脑,在命令提示符里运行 `build.bat`,
   产物在 `dist\WorkPlan.exe`。为了避免 Windows 批处理编码问题,
   打包脚本和 exe 文件名默认使用英文;打包完成后可以手动重命名。
2. GitHub Actions:推送 `v*` tag(或手动触发 workflow),
   在 Actions 页面下载 artifact「工作计划-windows-exe」。

首次启动约 2-4 秒(onefile 解压),属正常现象。
不要把 exe 放进 `Program Files`(目录不可写会拒绝启动并提示)。

仓库根目录已提供 `app.ico`,build.bat 会自动作为程序图标。

推荐从命令提示符运行,这样失败时能看到完整错误:

```bat
cd /d D:\工作计划Windows
build.bat
```

## 数据库版本和升级规则

数据文件固定放在:

```text
data/workplan.db
```

程序使用 SQLite 的 `PRAGMA user_version` 保存数据库版本。当前版本在
`app/data/db.py` 里:

```python
SCHEMA_VERSION = 1
```

启动时会执行:

```text
connect(data/workplan.db)
  -> 读取 PRAGMA user_version
  -> 如果版本低于 SCHEMA_VERSION,先备份,再逐个执行迁移
  -> 如果版本高于当前程序支持,拒绝启动,提示用户使用更新版本
```

升级前备份会自动写到:

```text
data/backups/workplan-YYYYMMDD-HHMMSS-before-upgrade-v旧版本-to-v新版本.db
```

### 以后新增数据库字段时怎么做

例如要从 v1 升到 v2:

1. 打开 `app/data/db.py`
2. 把 `SCHEMA_VERSION = 1` 改成 `SCHEMA_VERSION = 2`
3. 新增迁移函数:

```python
def _migrate_to_2(conn: sqlite3.Connection) -> None:
    conn.execute("ALTER TABLE plans ADD COLUMN priority INTEGER NOT NULL DEFAULT 0")
```

4. 把迁移函数加入 `MIGRATIONS`:

```python
MIGRATIONS: dict[int, Migration] = {
    1: _migrate_to_1,
    2: _migrate_to_2,
}
```

5. 增加/更新测试:

```bash
python -m pytest -q
```

迁移规则:

- 只允许追加迁移,不要修改已经发布过的旧迁移函数。
- 每个版本只做从上一个版本到当前版本的最小变更。
- 表结构变更必须给默认值,避免老数据升级失败。
- 不要在更新包里覆盖用户的 `data/` 文件夹。

## 给已使用用户发新版的流程

发布更新包时,不要带 `data/`。更新包只放程序文件,例如:

```text
WorkPlan.exe
_internal/
```

用户更新步骤:

```text
1. 关闭工作计划程序
2. 备份旧目录里的 data 文件夹
3. 用新版 WorkPlan.exe 和 _internal/ 覆盖旧程序文件
4. 保留原来的 data/workplan.db
5. 启动新版程序
```

如果新版包含数据库升级,程序会自动:

```text
1. 检测旧数据库版本
2. 在 data/backups/ 里生成升级前备份
3. 执行数据库迁移
4. 写入新的 PRAGMA user_version
```

如果升级后发现问题:

```text
1. 关闭程序
2. 从 data/backups/ 找到升级前备份
3. 复制为 data/workplan.db
4. 暂时换回旧版程序
```

### 最小源码压缩包

不带用户数据、不带虚拟环境:

```bash
7z a -t7z ../工作计划Windows-min.7z app run.py requirements.txt build.bat app.ico README.md .gitignore '-xr!__pycache__' '-xr!*.pyc' '-xr!.DS_Store'
```

## 冒烟测试清单(打包后在 Windows 上过一遍)

1. 新建分类并配色 -> 月历上颜色正确
2. 新建单日计划、跨天计划 -> 月历显示正确,跨周条带断行正常
3. 绑定文件夹和文件 -> 点击「打开」资源管理器跳转正确
4. 移走绑定的文件夹 -> 对话框中该行标红「路径不存在」
5. 标记完成 -> 灰色划线;制造逾期 -> 红点 + 重启弹提醒
6. 列表视图筛选、双击编辑
7. 关闭软件,拷贝整个目录到别处再运行 -> `data/workplan.db` 数据完整随行
8. 切换深色主题 -> 全部界面变色无遗漏;重启后仍是深色
