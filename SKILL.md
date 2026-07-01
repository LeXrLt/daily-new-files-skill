---
name: daily-new-files
description: >-
  扫描指定文件夹，按某一天的文件时间戳筛选新增文件，并生成 Markdown 每日新增文件日报。
  当用户要求“总结今天新增文件”、“生成文件日报”、“查看某目录本日/昨日/指定日期新增文件”、
  “what files were added today”等文件新增统计、目录新增摘要、每日文件 digest 场景时使用。
---

# 每日新增文件日报

使用本 skill 时，运行内置脚本统计指定目录在指定日期新增的文件，生成统一格式的
Markdown 日报，并把生成的日报文件原文回复给用户。

## 执行流程

1. 确认目标文件夹和日期。
   - 目标文件夹优先使用用户明确给出的路径。
   - 若用户未给路径，使用 `config.json` 中的 `folder`。
   - 若用户未给日期，使用本地日期的今天。
   - 用户使用“今天、昨天、本日”等相对日期时，转换为明确的 `YYYY-MM-DD` 日期。

2. 在 skill 根目录运行脚本。

   ```bash
   .venv/bin/python scripts/summarize_new_files.py --folder "<TARGET_FOLDER>" --date "<YYYY-MM-DD>"
   ```

   如果 `.venv/bin/python` 不存在，可改用：

   ```bash
   python3 scripts/summarize_new_files.py --folder "<TARGET_FOLDER>" --date "<YYYY-MM-DD>"
   ```

3. 根据用户需求追加参数。
   - `--recursive` / `--no-recursive`：是否扫描子文件夹，默认递归。
   - `--time-basis created`：按创建时间判断新增；当系统不支持创建时间时，脚本会回退到修改时间。
   - `--time-basis modified`：按修改时间判断新增。
   - `--output <PATH>`：指定日报输出路径；默认写入 `reports/<DATE>.md`。

4. 脚本会将日报打印到 stdout，同时写入 Markdown 文件；最后一行会输出：

   ```text
   REPORT_PATH: <生成的日报文件路径>
   ```

5. 读取 `REPORT_PATH` 指向的 Markdown 文件。

6. 直接把该 Markdown 文件的原始内容回复给用户。
   - 不要改写、摘要、翻译或重新排版日报内容。
   - 保留原文件中的标题、引用、列表、表格和页脚。
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
- 生成的日报文件是最终回复依据；如果 stdout 与文件内容不一致，以 `REPORT_PATH`
  指向的文件内容为准。
