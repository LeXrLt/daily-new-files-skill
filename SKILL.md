---
name: daily-new-files
description: >-
  查询指定文件夹在单日或指定日期范围内的新增、更新、修改文件，生成 Markdown 新增文件日报，
  并逐个浏览新增文件，为每个文件生成一句简短摘要，最终输出新增文件摘要汇总。
  任何需要查询“新增文件、今日新增、本周新增、指定日期范围新增、最近更新、文件变动、
  目录 digest、what files were added/updated”等本地文件新增或更新情况的任务都必须使用该技能。
---

# 新增文件摘要

使用本 skill 时，先运行内置脚本生成新增文件清单日报，再依据日报逐个浏览新增文件，
为每个文件写一句简短摘要，最后用 `templates/daily_summary_report.md` 生成新增文件
摘要汇总 Markdown，并把该摘要汇总文件的原始内容回复给用户。

## 执行流程

1. 确认目标文件夹、日期范围和时间口径。
   - 目标文件夹优先使用用户明确给出的路径。
   - 若用户未给路径，使用 `config.json` 中的 `folder`。
   - 若用户未给日期，使用本地日期的今天。
   - 若用户给出单日，起止日期都设为该日。
   - 若用户给出“今天、昨天、本周、近一周、最近 N 天”等相对日期，先转换为明确的 `YYYY-MM-DD` 起止日期，并采用闭区间。
   - 默认使用 `config.json` 中的 `time_basis`；用户说“修改、更新、modified、mtime”时，使用 `--time-basis modified`。

2. 在 skill 根目录运行脚本，生成新增文件清单日报。
   - 单日查询运行一次。
   - 日期范围查询按起止日期闭区间逐日运行一次，并收集每一天的 `REPORT_PATH`。

   ```bash
   python3 scripts/summarize_new_files.py --folder "<TARGET_FOLDER>" --date "<YYYY-MM-DD>"
   ```

   如存在 `.venv/bin/python`，可优先使用：

   ```bash
   .venv/bin/python scripts/summarize_new_files.py --folder "<TARGET_FOLDER>" --date "<YYYY-MM-DD>"
   ```

3. 根据用户需求追加脚本参数。
   - `--recursive` / `--no-recursive`：是否扫描子文件夹，默认递归。
   - `--time-basis created`：按创建时间判断新增；当系统不支持创建时间时，脚本会回退到修改时间。
   - `--time-basis modified`：按修改时间判断新增或更新。
   - `--output <PATH>`：指定单日新增文件清单日报输出路径；默认写入 `reports/<DATE>.md`。

4. 读取每次脚本最后一行输出的新增文件清单日报路径。

   ```text
   REPORT_PATH: <生成的新增文件清单日报路径>
   ```

5. 读取所有 `REPORT_PATH` 指向的 Markdown 文件，解析“文件清单”表格并合并。
   - 按表格顺序提取文件路径、类型、大小、时间。
   - 表格中的文件路径是相对目标文件夹的路径；使用“目标文件夹 + 相对路径”定位真实文件。
   - 日期范围内同一路径若重复出现，保留时间最新的一条，并在阅读说明中说明去重。
   - 忽略脚本输出中的“今天没有检测到新增文件”占位行。

6. 依次浏览新增文件，并为每个文件生成一句简短摘要。
   - 文本、Markdown、代码、JSON、CSV 等可读文件：读取内容后总结其主要用途或新增信息。
   - 体积很大的文本文件：优先浏览文件开头、结构、字段名或代表性片段，再给出谨慎摘要。
   - 二进制、图片、音视频、压缩包等不适合直接阅读的文件：根据文件名、扩展名、大小和可获得的元数据生成摘要，并在摘要中说明未读取正文。
   - 无法访问或读取失败的文件：保留该文件记录，并在摘要中说明失败原因。
   - 每个文件只写一句话，保持客观、简短，不要凭空推断文件内容。

7. 归纳摘要汇总内容。
   - `intro` 用一句话说明扫描目录、时间口径、日期范围、文件总数和主要集中方向，风格参考“按 X 本地文件修改时间查了，口径是 A 至 B。近一周共有 N 个文件更新，主要集中在 Y。”
   - `distribution_summary` 按有意义的目录、项目、公司、主题或文件类型分组，列出数量和主要内容。
   - `latest_items` 按文件时间倒序列出最近几项；相邻时间、同一主题的多文件可以合并成一条。
   - `notable_points` 提炼值得注意的模式，例如系统性更新、集中补充、最新增量、非正文文件或读取限制。
   - `file_summaries` 保留逐文件一句话摘要，格式建议为 `- YYYY-MM-DD HH:mm 路径：摘要`。

8. 使用 `templates/daily_summary_report.md` 作为格式模板，生成新增文件摘要汇总。
   - 单日默认输出到 `reports/<YYYY-MM-DD>-summary.md`。
   - 日期范围默认输出到 `reports/<START>_to_<END>-summary.md`。
   - `source_report_paths` 填入所有单日新增文件清单日报路径，可使用逗号分隔或 Markdown 列表。
   - `reading_notes` 填入阅读限制、跳过原因、去重说明或“全部新增文件均已浏览”。
   - 如果没有新增文件，各摘要区域写“未检测到新增文件”，并在 `reading_notes` 中说明口径。

9. 读取生成的新增文件摘要汇总 Markdown 文件，并直接把该文件的原始内容回复给用户。
   - 不要把最终回复替换为口语化总结。
   - 不要只回复单日新增文件清单日报。
   - 保留摘要汇总文件中的段落、标题、列表和页脚。
   - 除非用户另有要求，回复中不要额外添加解释性文字。

## 配置文件

如果需要默认配置，复制 `config.example.json` 为 `config.json` 并按需修改：

```json
{
  "folder": "/Users/yourname/Documents/Inbox",
  "recursive": true,
  "time_basis": "created",
  "ignore_hidden": true,
  "exclude_globs": [
    "**/.DS_Store",
    "**/node_modules/**",
    "**/.git/**"
  ]
}
```

字段说明：
- `folder`：要扫描的目标文件夹。
- `recursive`：是否递归扫描子文件夹。
- `time_basis`：使用 `created` 或 `modified` 判断文件是否属于当天新增或更新。
- `ignore_hidden`：是否忽略隐藏文件和隐藏目录。
- `exclude_globs`：需要排除的 glob 规则。

## 注意事项

- “新增/更新”完全依据文件时间戳判断；复制、移动、解压文件可能改变统计结果。
- 本 skill 不需要网络访问或 API key。
- 新增文件清单日报由脚本生成；新增文件摘要汇总由 agent 浏览文件后生成。
- 最终回复以生成的 `*-summary.md` 文件内容为准。
