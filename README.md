# daily-new-files skill

一个 Agent Skill：针对指定文件夹，**按文件时间戳**筛选出某一天新增的文件，
套用统一 Markdown 模板生成每日报告。用户向 AI 询问时，AI 读取 `SKILL.md`
并运行脚本，最后用自然语言汇报当日新增文件摘要。

## 目录结构

```
daily-new-files-skill/
├── SKILL.md                       # skill 入口，供 AI 读取并执行
├── scripts/summarize_new_files.py # 核心脚本
├── templates/daily_report.md      # Markdown 日报模板
├── config.example.json            # 配置示例（复制为 config.json）
├── reports/                       # 生成的日报输出目录
├── requirements.txt
└── README.md
```

## 环境搭建（macOS）

在项目根目录创建虚拟环境并激活：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # 目前无第三方依赖
```

## 配置

复制配置示例并按需修改：

```bash
cp config.example.json config.json
```

`config.json` 字段说明：

| 字段 | 说明 |
|------|------|
| `folder` | 要扫描的目标文件夹（绝对路径） |
| `recursive` | 是否递归扫描子文件夹 |
| `time_basis` | `created`（创建时间，macOS 用 `st_birthtime`）或 `modified`（修改时间） |
| `ignore_hidden` | 是否忽略以 `.` 开头的隐藏文件/目录 |
| `exclude_globs` | 需要排除的 glob 模式列表 |

## 使用

```bash
# 使用 config.json 中的 folder，统计今天新增
.venv/bin/python scripts/summarize_new_files.py

# 指定文件夹与日期
.venv/bin/python scripts/summarize_new_files.py \
  --folder "/Users/yourname/Documents/Inbox" \
  --date 2026-07-01

# 仅当前文件夹、按修改时间统计
.venv/bin/python scripts/summarize_new_files.py --no-recursive --time-basis modified
```

报告会同时打印到终端并写入 `reports/<日期>.md`，最后一行以
`REPORT_PATH: ...` 输出报告路径，便于 AI 读取。

## 通过 AI（skill）使用

将本项目作为 skill 提供给支持 Agent Skills 的助手后，直接询问：

> "总结一下今天 Inbox 里新增的文件"

助手会读取 `SKILL.md`，运行脚本并汇报摘要。

## 可选：每天自动生成（launchd / cron）

若希望每天定时生成日报，可在 mac 上用 `cron`：

```bash
# 每天 22:00 运行，crontab -e 添加：
0 22 * * * /path/to/daily-new-files-skill/.venv/bin/python /path/to/daily-new-files-skill/scripts/summarize_new_files.py
```
