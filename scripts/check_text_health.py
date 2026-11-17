#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Name        : check_text_health.py
# Description : 只读检查文本文件的编码、BOM、换行、NUL、疑似乱码与 .gitignore 红线；不修改任何文件
# Author      : Doubao
# Version     : 1.1.0
# Update      : 2026-11-17
# Usage       : python scripts/check_text_health.py PATH... [--gitignore] [--git] [--json] [--strict]
# Dependencies: Python 3.8+ 标准库；--git 需要 git 可执行文件
"""Read-only text health checks for project-spec.

Exit codes:
  0  no errors (warnings allowed unless --strict)
  1  errors found, or warnings found with --strict
  2  usage / path error
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TEXT_SUFFIXES = {
    ".md", ".markdown", ".txt", ".rst", ".py", ".pyi", ".r", ".sh", ".bash", ".zsh",
    ".ps1", ".psm1", ".bat", ".cmd", ".csv", ".tsv", ".json", ".jsonl", ".yml", ".yaml",
    ".toml", ".ini", ".cfg", ".conf", ".xml", ".html", ".htm", ".css", ".scss", ".js",
    ".jsx", ".ts", ".tsx", ".sql", ".tex", ".bib", ".gitignore", ".gitattributes",
    ".editorconfig", ".dockerfile", ".mk", ".h", ".c", ".cc", ".cpp", ".hpp", ".java",
    ".go", ".rs", ".swift", ".kt", ".m", ".mm", ".do", ".sas", ".stan", ".qmd", ".rmd",
    ".ipynb", ".log", ".tsv", ".srt", ".vtt",
}
TEXT_NAMES = {
    "Dockerfile", "Makefile", "LICENSE", "README", "VERSION", "AUTHORS", "CHANGELOG",
    "CONTRIBUTING", "CODEOWNERS", ".gitignore", ".gitattributes", ".editorconfig",
}
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", "dist",
    "build", ".mypy_cache", ".pytest_cache", ".ipynb_checkpoints", ".idea", ".vscode",
}
CRLF_OK_SUFFIXES = {".ps1", ".psm1", ".bat", ".cmd"}
RED_LINES = {
    "*.log": "全局忽略 *.log 可能排除必要运行/审计日志；改为窄路径或按用途保留",
    "logs": "全局忽略 logs/ 可能隐藏必要执行证据；改为具体运行目录或按用途保留",
    "_*.py": "_*.py 会误匹配 __init__.py 等正式源码；用已核实目录表达临时用途",
    "_*.ps1": "_*.ps1 可能误匹配正式脚本；用已核实目录表达临时用途",
    "data/raw": "默认排除整个 data/raw/ 可能丢失复现输入或样例；改为窄规则并保留来源说明",
    "archive": "全局忽略 archive/ 可能隐藏需要保留的历史证据；改为具体子目录",
}
RED_ALIASES = {
    "*.log": {"*.log", "**/*.log"},
    "logs": {"logs", "**/logs"},
    "_*.py": {"_*.py", "**/_*.py"},
    "_*.ps1": {"_*.ps1", "**/_*.ps1"},
    "data/raw": {"data/raw", "**/data/raw"},
    "archive": {"archive", "**/archive"},
}
MOJIBAKE_MARKERS = (
    ("\ufffd", "error", "Unicode 替换字符 U+FFFD，通常表示解码失败"),
    ("\u9535\u65a4\u62f7", "error", "典型 GBK/UTF-8 乱码串"),
    ("\ufffd\ufffd\ufffd\ufffd", "error", "典型乱码替换串"),
    ("\u9225", "error", "典型引号乱码"),
    ("\u00ef\u00bb\u00bf", "warning", "BOM 被当作可见文本写入"),
)


def add_issue(issues: list[dict], level: str, path: Path, code: str, message: str, line: int | None = None) -> None:
    issues.append({
        "level": level,
        "path": str(path),
        "line": line,
        "code": code,
        "message": message,
    })


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES


def collect_files(raw_paths: list[str], explicit_gitignore: bool) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    missing: list[str] = []
    for raw in raw_paths:
        path = Path(raw).expanduser().resolve()
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for root, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for name in names:
                    candidate = Path(root) / name
                    if name == ".gitignore" or is_text_candidate(candidate):
                        files.append(candidate)
        else:
            missing.append(str(path))
    # Explicit files are always checked; --gitignore also treats a single explicit file as a rules file.
    return sorted(set(files)), missing


def decode_text(path: Path, data: bytes, issues: list[dict]) -> tuple[str, bool]:
    bom = None
    payload = data
    if data.startswith(b"\xef\xbb\xbf"):
        bom = "UTF-8 BOM"
        payload = data[3:]
    elif data.startswith(b"\xff\xfe"):
        bom = "UTF-16LE BOM"
    elif data.startswith(b"\xfe\xff"):
        bom = "UTF-16BE BOM"
    if bom:
        add_issue(issues, "error", path, "BOM", f"检测到 {bom}；项目默认要求 UTF-8 no BOM")
    try:
        if bom == "UTF-16LE BOM":
            return data.decode("utf-16-le"), False
        if bom == "UTF-16BE BOM":
            return data.decode("utf-16-be"), False
        return payload.decode("utf-8"), False
    except UnicodeDecodeError as exc:
        line = payload[: exc.start].count(b"\n") + 1
        add_issue(
            issues,
            "error",
            path,
            "UTF8",
            f"严格 UTF-8 解码失败：字节偏移 {exc.start}（行 {line}），{exc.reason}",
            line,
        )
        # Best-effort fallback so line-level checks (e.g. .gitignore red lines) can still run.
        return payload.decode("utf-8", errors="replace"), True


def check_mojibake(path: Path, text: str, issues: list[dict], allow: list[str]) -> None:
    if allow:
        lines = [
            (number, line)
            for number, line in enumerate(text.splitlines(), 1)
            if not any(token in line for token in allow)
        ]
    else:
        lines = list(enumerate(text.splitlines(), 1))
    for number, line in lines:
        for marker, level, message in MOJIBAKE_MARKERS:
            if marker in line:
                add_issue(issues, level, path, "MOJIBAKE", f"{message}：{marker!r}", number)
    latin1_hits = text.count("\u00c3") + text.count("\u00c2")
    if latin1_hits >= 2:
        first = next((i for i, line in enumerate(text.splitlines(), 1) if "\u00c3" in line or "\u00c2" in line), None)
        add_issue(
            issues,
            "warning",
            path,
            "MOJIBAKE-LATIN1",
            f"疑似 UTF-8 被按 Latin-1/Windows-1252 解码：高位字符出现 {latin1_hits} 次",
            first,
        )


def normalize_rule(line: str) -> str:
    value = line.strip().replace("\\", "/")
    value = value.lstrip("/").rstrip("/")
    return value


def check_gitignore_lines(path: Path, text: str, issues: list[dict]) -> list[str]:
    hits: list[str] = []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        normalized = normalize_rule(stripped)
        for red, message in RED_LINES.items():
            if normalized in RED_ALIASES[red]:
                add_issue(issues, "warning", path, "GITIGNORE-RED", f"`{stripped}`：{message}", number)
                hits.append(red)
    return sorted(set(hits))


def git_ls_files(cwd: Path) -> tuple[str | None, list[str], str | None]:
    git = shutil.which("git") or "git"
    try:
        top = subprocess.run(
            [git, "rev-parse", "--show-toplevel"], cwd=str(cwd), text=True, encoding="utf-8", capture_output=True
        )
        if top.returncode != 0:
            return None, [], "not a Git repository"
        root = top.stdout.strip()
        listed = subprocess.run(
            [git, "ls-files"], cwd=root, text=True, encoding="utf-8", capture_output=True
        )
        if listed.returncode != 0:
            return root, [], "git ls-files failed"
        return root, [line for line in listed.stdout.splitlines() if line], None
    except FileNotFoundError:
        return None, [], "git executable not found"


def tracked_matches(red: str, tracked: list[str]) -> list[str]:
    matched: list[str] = []
    for name in tracked:
        base = os.path.basename(name)
        if red == "*.log":
            if name.endswith(".log"):
                matched.append(name)
        elif red == "logs":
            if name.startswith("logs/") or "/logs/" in name:
                matched.append(name)
        elif red == "_*.py":
            if base.startswith("_") and base.endswith(".py"):
                matched.append(name)
        elif red == "_*.ps1":
            if base.startswith("_") and base.endswith(".ps1"):
                matched.append(name)
        elif red == "data/raw":
            if name.startswith("data/raw/") or "/data/raw/" in name:
                matched.append(name)
        elif red == "archive":
            if name.startswith("archive/") or "/archive/" in name:
                matched.append(name)
    return matched


def check_file(path: Path, args: argparse.Namespace) -> list[dict]:
    issues: list[dict] = []
    try:
        data = path.read_bytes()
    except OSError as exc:
        add_issue(issues, "error", path, "READ", f"无法读取：{exc}")
        return issues
    if len(data) > args.max_bytes:
        add_issue(
            issues,
            "warning",
            path,
            "SIZE",
            f"文件 {len(data)} 字节，超过 --max-bytes={args.max_bytes}；跳过内容检查",
        )
        return issues
    text, decode_failed = decode_text(path, data, issues)
    if not data.startswith((b"\xff\xfe", b"\xfe\xff")):
        nul_count = data.count(b"\x00")
        if nul_count:
            add_issue(issues, "error", path, "NUL", f"检测到 {nul_count} 个 NUL (0x00) 字节")
    crlf = data.count(b"\r\n")
    lone_cr = data.count(b"\r") - crlf
    if crlf and path.suffix.lower() not in CRLF_OK_SUFFIXES:
        add_issue(
            issues,
            "warning",
            path,
            "CRLF",
            f"检测到 {crlf} 处 CRLF；项目默认 LF（.ps1/.bat/.cmd 可保留 CRLF）",
        )
    if lone_cr:
        add_issue(issues, "warning", path, "CR", f"检测到 {lone_cr} 个单独 CR；可能造成跨平台换行异常")
    trailing = [number for number, line in enumerate(text.splitlines(), 1) if line.endswith((" ", "\t"))]
    if trailing:
        preview = ", ".join(str(number) for number in trailing[:8])
        add_issue(
            issues,
            "warning",
            path,
            "TRAILING",
            f"行尾空格/制表符 {len(trailing)} 行：{preview}{' ...' if len(trailing) > 8 else ''}",
        )
    if not args.no_mojibake and not decode_failed:
        check_mojibake(path, text, issues, args.allow)
    if args.gitignore and (path.name == ".gitignore" or path.is_file() and args.paths and len(args.paths) == 1):
        red_hits = check_gitignore_lines(path, text, issues)
        if args.git:
            root, tracked, error = git_ls_files(path.parent)
            if error:
                add_issue(issues, "warning", path, "GIT", f"--git 检查未完成：{error}")
            else:
                for red in red_hits:
                    matched = tracked_matches(red, tracked)
                    if matched:
                        preview = ", ".join(matched[:5])
                        add_issue(
                            issues,
                            "warning",
                            path,
                            "GIT-TRACKED",
                            f"`{red}` 影响已跟踪文件（.gitignore 不会自动移除）：{preview}{' ...' if len(matched) > 5 else ''}",
                        )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="只读检查文本文件的编码、BOM、换行、NUL、疑似乱码与 .gitignore 红线。"
    )
    parser.add_argument("paths", nargs="*", default=["."], help="文件或目录；默认当前目录")
    parser.add_argument("--gitignore", action="store_true", help="检查 .gitignore 的全局忽略红线")
    parser.add_argument("--git", action="store_true", help="配合 --gitignore 列出被红线规则影响的已跟踪文件")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--strict", action="store_true", help="把 warning 也视为失败")
    parser.add_argument("--no-mojibake", action="store_true", help="关闭疑似乱码启发式检查")
    parser.add_argument("--allow", default="", help="逗号分隔的白名单片段；包含这些片段的行跳过乱码检查")
    parser.add_argument("--max-bytes", type=int, default=20 * 1024 * 1024, help="单文件检查上限，默认 20 MiB")
    parser.add_argument("--version", action="version", version="check_text_health.py 1.1.0")
    args = parser.parse_args()
    args.paths = args.paths or ["."]
    args.allow = [token.strip() for token in args.allow.split(",") if token.strip()]

    files, missing = collect_files(args.paths, args.gitignore)
    issues: list[dict] = []
    for item in missing:
        issues.append({
            "level": "error",
            "path": item,
            "line": None,
            "code": "PATH",
            "message": "路径不存在",
        })
    for path in files:
        issues.extend(check_file(path, args))

    errors = sum(1 for issue in issues if issue["level"] == "error")
    warnings = sum(1 for issue in issues if issue["level"] == "warning")
    report = {
        "checked": len(files),
        "errors": errors,
        "warnings": warnings,
        "issues": issues,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for issue in issues:
            location = f"{issue['path']}:{issue['line']}" if issue["line"] else issue["path"]
            print(f"[{issue['level'].upper()}] {location} {issue['code']}: {issue['message']}")
        print(f"checked={len(files)} errors={errors} warnings={warnings}")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
