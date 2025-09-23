# 目标管理器

这是一个简单的命令行目标管理器，可以在电脑上运行，用于记录每日、每周、每月和每年的目标完成情况。程序会把数据保存在当前用户的数据目录（例如 Windows 的 `%APPDATA%\GoalManager` 或 Linux 的 `~/.local/share/goal_manager`）下的 `goal_manager.json`，因此多次运行都会保留历史。

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

## 数据存储位置

程序默认把数据写入：

- **Windows**：`%APPDATA%\GoalManager\goal_manager.json`（若 `%APPDATA%` 不存在，则会回退到 `%LOCALAPPDATA%`）。
- **macOS / Linux**：`~/.local/share/goal_manager/goal_manager.json`，或遵循 `XDG_DATA_HOME` 环境变量指定的目录。

如果想把数据放到其它位置，可在启动命令前设置环境变量 `GOAL_MANAGER_DATA` 指向自定义目录，例如：

```bash
GOAL_MANAGER_DATA=~/Documents/goal-data python goal_manager.py remind
```

## 打包为 Windows 可执行文件

仓库提供了 `build_exe.py` 脚本，用于调用 [PyInstaller](https://pyinstaller.org/) 打包成独立的 `GoalManager.exe`。在 Windows 机器（或安装了 PyInstaller 的环境）上依次执行：

1. 安装依赖：

   ```powershell
   pip install pyinstaller
   ```

2. 运行打包脚本：

   ```powershell
   python build_exe.py
   ```

   完成后，可在仓库根目录的 `dist/GoalManager.exe` 找到可执行文件，把它复制到任意位置即可运行。

若需要重新打包，只需再次运行脚本，它会自动清理旧的构建产物。
