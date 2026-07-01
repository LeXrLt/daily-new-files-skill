---
name: daily-new-files
description: >-
  扫描指定文件夹，按某一天的文件时间戳筛选新增文件，生成 Markdown 新增文件日报，
  并逐个浏览新增文件，为每个文件生成一句简短摘要，最终输出每日新增文件摘要汇总。
  当用户要求“总结今天新增文件”、“生成文件日报”、“查看某目录本日/昨日/指定日期新增文件”、
  “总结新增文件内容”、“what files were added today”等文件新增统计、目录新增摘要、
  每日文件 digest 场景时使用。
---

# 每日新增文件摘要

使用本 skill 时，先运行内置脚本生成新增文件清单日报，再依据日报逐个浏览新增文件，
为每个文件写一句简短摘要，最后用 `templates/daily_summary_report.md` 生成每日新增文件
摘要汇总 Markdown，并把该摘要汇总文件的原始内容回复给用户。

## 执行流程

1. 确认目标文件夹和日期。
   - 目标文件夹优先使用用户明确给出的路径。
   - 若用户未给路径，使用 `config.json` 中的 `folder`。
   - 若用户未给日期，使用本地日期的今天。
   - 用户使用“今天、昨天、本日”等相对日期时，转换为明确的 `YYYY-MM-DD` 日期。

2. 在 skill 根目录运行脚本，生成新增文件清单日报。

   ```bash
   .venv/bin/python scripts/summarize_new_files.py --folder "<TARGET_FOLDER>" --date "<YYYY-MM-DD>"
   ```

   如果 `.venv/bin/python` 不存在，可改用：

   ```bash
   python3 scripts/summarize_new_files.py --folder "<TARGET_FOLDER>" --date "<YYYY-MM-DD>"
   ```

3. 根据用户需求追加脚本参数。
   - `--recursive` / `--no-recursive`：是否扫描子文件夹，默认递归。
   - `--time-basis created`：按创建时间判断新增；当系统不支持创建时间时，脚本会回退到修改时间。
   - `--time-basis modified`：按修改时间判断新增。
   - `--output <PATH>`：指定新增文件清单日报输出路径；默认写入 `reports/<DATE>.md`。

4. 读取脚本最后一行输出的新增文件清单日报路径。

   ```text
   REPORT_PATH: <生成的新增文件清单日报路径>
   ```

5. 读取 `REPORT_PATH` 指向的 Markdown 文件，解析“文件清单”表格。
   - 按表格顺序处理每个新增文件。
   - 表格中的文件路径是相对目标文件夹的路径；使用“目标文件夹 + 相对路径”定位真实文件。
   - 保留文件的序号、路径、类型、大小、时间，用于后续摘要汇总。

6. 依次浏览新增文件，并为每个文件生成一句简短摘要。
   - 文本、Markdown、代码、JSON、CSV 等可读文件：读取内容后总结其主要用途或新增信息。
   - 体积很大的文本文件：优先浏览文件开头、结构、字段名或代表性片段，再给出谨慎摘要。
   - 二进制、图片、音视频、压缩包等不适合直接阅读的文件：根据文件名、扩展名、大小和可获得的元数据生成摘要，并在摘要中说明未读取正文。
   - 无法访问或读取失败的文件：保留该文件记录，并在摘要中说明失败原因。
   - 每个文件只写一句话，保持客观、简短，不要凭空推断文件内容。

7. 使用 `templates/daily_summary_report.md` 作为格式模板，生成每日新增文件摘要汇总。
   - 默认输出到 `reports/<YYYY-MM-DD>-summary.md`。
   - 摘要清单应包含：序号、文件、类型、大小、时间、一句话摘要。
   - `summary_rows` 每行使用 Markdown 表格行；表格单元中的 `|` 要转义为 `\|`，换行要压成空格。
   - `source_report_path` 填入第 4 步得到的新增文件清单日报路径。
   - `reading_notes` 填入阅读限制、跳过原因或“全部新增文件均已浏览”。
   - 如果没有新增文件，保留表头，并在 `reading_notes` 中说明当天未检测到新增文件。

8. 读取生成的每日新增文件摘要汇总 Markdown 文件，并直接把该文件的原始内容回复给用户。
   - 不要把最终回复替换为口语化总结。
   - 不要只回复第 4 步生成的新增文件清单日报。
   - 保留摘要汇总文件中的标题、引用、列表、表格和页脚。
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
- `time_basis`：使用 `created` 或 `modified` 判断文件是否属于当天新增。
- `ignore_hidden`：是否忽略隐藏文件和隐藏目录。
- `exclude_globs`：需要排除的 glob 规则。

## 注意事项

- “新增”完全依据文件时间戳判断；复制、移动、解压文件可能改变统计结果。
- 本 skill 不需要网络访问或 API key。
- 新增文件清单日报由脚本生成；每日新增文件摘要汇总由 agent 浏览文件后生成。
- 最终回复以 `reports/<YYYY-MM-DD>-summary.md` 的文件内容为准。
