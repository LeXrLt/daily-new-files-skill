#!/usr/bin/env python3
"""Summarize files newly added to a folder on a given day, based on timestamps.

Pure standard library. Designed to run on macOS (uses st_birthtime for creation
time when available, falls back to modification time).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
from collections import defaultdict
from datetime import datetime, date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "templates" / "daily_report.md"
CONFIG_PATH = ROOT / "config.json"
DEFAULT_REPORTS_DIR = ROOT / "reports"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Summarize newly added files for a day.")
    p.add_argument("--folder", help="Target folder to scan.")
    p.add_argument("--date", help="Day to report on, format YYYY-MM-DD (default: today).")
    p.add_argument("--output", help="Output report path (default: reports/<DATE>.md).")
    p.add_argument("--time-basis", choices=["created", "modified"], default=None,
                   help="Which timestamp decides 'new'. Default: created.")
    p.add_argument("--recursive", dest="recursive", action="store_true", default=None,
                   help="Scan subfolders (default).")
    p.add_argument("--no-recursive", dest="recursive", action="store_false",
                   help="Do not scan subfolders.")
    return p.parse_args()


def get_file_time(path: Path, basis: str) -> float:
    st = path.stat()
    if basis == "created":
        # macOS provides st_birthtime; fall back to mtime elsewhere.
        return getattr(st, "st_birthtime", st.st_mtime)
    return st.st_mtime


def human_size(num: int) -> str:
    size = float(num)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def is_excluded(rel_path: str, name: str, ignore_hidden: bool, exclude_globs: list[str]) -> bool:
    if ignore_hidden and name.startswith("."):
        return True
    for pattern in exclude_globs:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
            return True
    return False


def collect_files(folder: Path, recursive: bool, ignore_hidden: bool,
                  exclude_globs: list[str]) -> list[Path]:
    results: list[Path] = []
    if recursive:
        for dirpath, dirnames, filenames in os.walk(folder):
            if ignore_hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fn in filenames:
                fp = Path(dirpath) / fn
                rel = str(fp.relative_to(folder))
                if is_excluded(rel, fn, ignore_hidden, exclude_globs):
                    continue
                results.append(fp)
    else:
        for fp in folder.iterdir():
            if fp.is_file() and not is_excluded(fp.name, fp.name, ignore_hidden, exclude_globs):
                results.append(fp)
    return results


def build_file_table(rows: list[dict], folder: Path) -> str:
    if not rows:
        return "_今天没有检测到新增文件。_"
    lines = ["| # | 文件 | 类型 | 大小 | 时间 |", "|---|------|------|------|------|"]
    for i, r in enumerate(rows, 1):
        rel = os.path.relpath(r["path"], folder)
        lines.append(
            f"| {i} | `{rel}` | {r['ext'] or '(无)'} | {human_size(r['size'])} | {r['time']:%H:%M:%S} |"
        )
    return "\n".join(lines)


def build_type_table(rows: list[dict]) -> str:
    if not rows:
        return "_无_"
    stats: dict[str, dict] = defaultdict(lambda: {"count": 0, "size": 0})
    for r in rows:
        key = r["ext"] or "(无扩展名)"
        stats[key]["count"] += 1
        stats[key]["size"] += r["size"]
    lines = ["| 类型 | 数量 | 大小 |", "|------|------|------|"]
    for ext, s in sorted(stats.items(), key=lambda kv: kv[1]["count"], reverse=True):
        lines.append(f"| {ext} | {s['count']} | {human_size(s['size'])} |")
    return "\n".join(lines)


def type_summary(rows: list[dict]) -> str:
    if not rows:
        return "无"
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        counts[r["ext"] or "(无扩展名)"] += 1
    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return "、".join(f"{ext}×{n}" for ext, n in top)


def main() -> None:
    args = parse_args()
    cfg = load_config()

    folder_str = args.folder or cfg.get("folder")
    if not folder_str:
        raise SystemExit("错误：未指定目标文件夹。请用 --folder 或在 config.json 设置 folder。")
    folder = Path(folder_str).expanduser().resolve()
    if not folder.is_dir():
        raise SystemExit(f"错误：文件夹不存在或不是目录：{folder}")

    target_day = (
        datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    )
    day_start = datetime.combine(target_day, datetime.min.time())
    day_end = day_start + timedelta(days=1)

    recursive = args.recursive if args.recursive is not None else cfg.get("recursive", True)
    time_basis = args.time_basis or cfg.get("time_basis", "created")
    ignore_hidden = cfg.get("ignore_hidden", True)
    exclude_globs = cfg.get("exclude_globs", [])

    rows: list[dict] = []
    for fp in collect_files(folder, recursive, ignore_hidden, exclude_globs):
        try:
            ts = get_file_time(fp, time_basis)
            when = datetime.fromtimestamp(ts)
        except (OSError, ValueError):
            continue
        if day_start <= when < day_end:
            rows.append({
                "path": fp,
                "ext": fp.suffix.lower(),
                "size": fp.stat().st_size,
                "time": when,
            })
    rows.sort(key=lambda r: r["time"])

    total_size = sum(r["size"] for r in rows)
    basis_label = "按创建时间" if time_basis == "created" else "按修改时间"
    scope_label = "含子文件夹" if recursive else "仅当前文件夹"

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    report = template.format(
        date=target_day.isoformat(),
        folder=folder,
        time_basis_label=basis_label,
        scope_label=scope_label,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_count=len(rows),
        total_size_human=human_size(total_size),
        type_summary=type_summary(rows),
        file_table=build_file_table(rows, folder),
        type_table=build_type_table(rows),
    )

    output = Path(args.output).expanduser() if args.output else DEFAULT_REPORTS_DIR / f"{target_day.isoformat()}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nREPORT_PATH: {output.resolve()}")


if __name__ == "__main__":
    main()
