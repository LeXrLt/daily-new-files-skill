---
name: daily-new-files
description: >-
  Summarize files newly added to a specified folder for a given day (based on
  file timestamps) and produce a clean Markdown daily report. Use this skill
  whenever the user asks for a daily summary / digest of new files in a folder,
  e.g. "总结今天新增的文件", "生成今日文件日报", "what files were added today".
---

# Daily New Files Summary

This skill scans a target folder, finds files whose timestamp falls within a
given day, and renders a unified Markdown daily report from a template.

## When to use

Trigger this skill when the user wants a report of files that were **newly
added** to a folder on a specific day (default: today).

## How to run

1. Make sure the virtual environment exists (see `README.md`). Use the venv's
   Python interpreter to run the script:

   ```bash
   .venv/bin/python scripts/summarize_new_files.py --folder "<TARGET_FOLDER>"
   ```

2. Common options:

   - `--folder PATH`   Target folder to scan. If omitted, the script reads
     `folder` from `config.json` (copy from `config.example.json`).
   - `--date YYYY-MM-DD`  The day to report on. Defaults to today (local time).
   - `--recursive` / `--no-recursive`  Whether to scan subfolders. Default: recursive.
   - `--time-basis {created,modified}`  Which timestamp decides "new". Default:
     `created` (falls back to modified time when creation time is unavailable).
   - `--output PATH`  Where to write the report. Defaults to
     `reports/<DATE>.md`.

3. The script prints the report to stdout AND writes it to the reports folder.

## How to report back to the user

After running the script:

1. Read the generated Markdown report (path is printed on the last line as
   `REPORT_PATH: ...`).
2. Present a concise natural-language summary to the user: how many new files,
   their total size, notable file types, and highlight anything interesting.
3. Offer to open the full report or re-run for a different date/folder.

## Notes

- "New" is determined purely by file timestamps, so copying/moving files may
  affect results.
- No network access or API keys are required.
