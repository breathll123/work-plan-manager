# 工作计划

本地便携版工作计划管理软件:分类管理、月历/列表视图、文件夹绑定一键跳转、
启动待办提醒、浅色/深色主题。数据存在软件同目录的 `workplan.db`,
整个文件夹拷走即可迁移。

## 开发(macOS / Windows / Linux)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # Windows: .venv\Scripts\pip
.venv/bin/python -m app.main                # 运行
.venv/bin/pytest -q                         # 测试
```

## 打包成 Windows exe

PyInstaller 不支持跨平台打包,必须在 Windows 上执行(二选一):

1. 本机打包:把仓库拷到 Windows 电脑,双击 `build.bat`,
   产物在 `dist\工作计划.exe`。
2. GitHub Actions:推送 `v*` tag(或手动触发 workflow),
   在 Actions 页面下载 artifact「工作计划-windows-exe」。

首次启动约 2-4 秒(onefile 解压),属正常现象。
不要把 exe 放进 `Program Files`(目录不可写会拒绝启动并提示)。

可选:仓库根目录放一个 `app.ico`,build.bat 会自动作为程序图标。

## 冒烟测试清单(打包后在 Windows 上过一遍)

1. 新建分类并配色 -> 月历上颜色正确
2. 新建单日计划、跨天计划 -> 月历显示正确,跨周条带断行正常
3. 绑定文件夹和文件 -> 点击「打开」资源管理器跳转正确
4. 移走绑定的文件夹 -> 对话框中该行标红「路径不存在」
5. 标记完成 -> 灰色划线;制造逾期 -> 红点 + 重启弹提醒
6. 列表视图筛选、双击编辑
7. 关闭软件,拷贝整个目录到别处再运行 -> 数据完整随行
8. 切换深色主题 -> 全部界面变色无遗漏;重启后仍是深色
