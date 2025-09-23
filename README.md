# 目标管理器

这是一个简单的命令行目标管理器，可以在电脑上运行，用于记录每日、每周、每月和每年的目标完成情况。程序会把数据保存在同目录下的 `goal_manager.json` 中，因此多次运行都会保留历史。

## 使用方法

1. **添加目标**

   ```bash
   python goal_manager.py add "锻炼" --frequency daily
   python goal_manager.py add "整理财务" --frequency monthly
   ```

2. **查看目标和今日状态**

   ```bash
   python goal_manager.py list
   ```

3. **每日提醒**：运行下面的命令，程序会询问每个目标今天（或当期）是否完成，按下 `y`/`n` 或直接回车跳过。

   ```bash
   python goal_manager.py remind
   ```

4. **手动修改状态**

   ```bash
   python goal_manager.py check "锻炼" --frequency daily --done
   python goal_manager.py check "整理财务" --frequency monthly --not-done
   ```

建议把提醒命令加入系统的计划任务（如 Windows 任务计划程序、macOS/Linux 的 cron），每天自动运行一次即可完成日常提醒。

## 运行 Web 界面

除了命令行工具，还可以启动一个基于 Flask 的简单网页来管理目标：

1. 安装依赖（如果尚未安装）：

   ```bash
   pip install flask
   ```

2. 在项目根目录启动开发服务器：

   ```bash
   FLASK_APP=web_app.py flask run
   ```

   或者使用较新的写法：

   ```bash
   python -m flask --app web_app run --debug
   ```

3. 打开浏览器访问 `http://127.0.0.1:5000/`，即可通过网页查看、添加或勾选目标。

部署到服务器时，可以将 `web_app:app` 作为 WSGI 入口，交给如 Gunicorn、uWSGI 等 WSGI 容器或任何支持 WSGI 的平台来运行。
