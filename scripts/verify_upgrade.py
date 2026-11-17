#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Name: verify_upgrade.py
# Description: Verify the current project-spec snapshot read-only; write isolated Git fixtures only.
# Author: Codex
# Version: 1.1.0
# Update: 2026-11-17
# Usage: python3 scripts/verify_upgrade.py PATH_TO_SKILL
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
base = 'e4222a610dac8c07cdb4cffe8f11d1525416465a'
env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_OPTIONAL_LOCKS='0')

def git(cwd, *args, allowed=(0,)):
    result = subprocess.run(['git', '-c', 'core.excludesFile=' + os.devnull, '-c', 'core.hooksPath=' + os.devnull, *args], cwd=cwd, env=env, text=True, encoding='utf-8', capture_output=True)
    assert result.returncode in allowed, (args, result.returncode, result.stdout, result.stderr)
    return result

probe = git(root, 'rev-parse', '--show-toplevel', allowed=(0, 128))
has_git = probe.returncode == 0 and Path(probe.stdout.strip()).resolve() == root
files = sorted(root.rglob('*.md'))
files = [p for p in files if '.git' not in p.relative_to(root).parts]
links = 0
for path in files:
    data = path.read_bytes()
    assert not data.startswith(b'\xef\xbb\xbf') and b'\r' not in data, path
    content = data.decode('utf-8')
    assert re.search(r'^> 版本: v\d+\.\d+\.\d+', content, re.M), path
    assert re.search(r'^> 更新日期: \d{4}-\d{2}-\d{2}', content, re.M), path
    assert '| 版本 | 日期 | 修改说明 | 作者 |' in content, path
    opened = None
    for line in content.splitlines():
        fence = re.match(r'^(`{3,}|~{3,})', line)
        if fence:
            marker = fence.group(1)
            if opened is None:
                opened = marker
            elif marker[0] == opened[0] and len(marker) >= len(opened):
                opened = None
        assert not line.endswith((' ', '\t')), (path, line)
    assert opened is None, (path, 'unclosed fence')
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', content):
        if '://' not in target and not target.startswith('#'):
            assert (path.parent / target.split('#')[0]).exists(), (path, target)
            links += 1
    rel = str(path.relative_to(root))
    if not has_git or not git(root, 'ls-files', '--', rel).stdout:
        whitespace = git(root, 'diff', '--no-index', '--check', os.devnull, rel, allowed=(0, 1))
        assert not whitespace.stdout and not whitespace.stderr, (path, whitespace.stdout, whitespace.stderr)
assert files and 'name: project-spec\n' in (root / 'SKILL.md').read_text(encoding='utf-8')
assert (root / 'SKILL.md').read_text(encoding='utf-8').startswith('---\n')
assert (root / 'scripts/check_text_health.py').is_file()
head = None
base_available = False
if has_git:
    git(root, 'diff', '--check')
    head = git(root, 'rev-parse', 'HEAD').stdout.strip()
    base_available = git(root, 'cat-file', '-e', base + '^{commit}', allowed=(0, 1, 128)).returncode == 0
    if base_available:
        git(root, 'merge-base', '--is-ancestor', base, 'HEAD')
    assert not git(root, 'diff', '--cached', '--name-only').stdout
assert not list(root.rglob('.gitignore'))
print(json.dumps({'static': 'PASS', 'markdown_files': len(files), 'local_links': links, 'head_commit': head, 'base_ancestor_checked': base if base_available else None, 'staged_changes': 0 if has_git else None, 'actual_gitignore_files': 0}, ensure_ascii=False))

with tempfile.TemporaryDirectory(prefix='project-spec-fixture-') as temp:
    fixture = Path(temp)
    git(fixture, 'init', '-q')
    for name, value in {'user.txt': 'baseline\n', 'scripts/analyze.py': 'print(1)\n', 'scratch/tracked.tmp': 'tracked evidence\n', 'src/package/__init__.py': '', 'src/_helpers.py': '', 'docs/audit/run.log': 'necessary log\n', 'data/raw/README.md': 'reproduction source\n', 'scratch/cache.tmp': '', 'runs/local-debug/debug.log': '', '__pycache__/a.pyc': '', '.venv/pyvenv.cfg': ''}.items():
        dest = fixture / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(value)
    git(fixture, 'add', '--', 'user.txt', 'scripts/analyze.py', 'scratch/tracked.tmp')
    git(fixture, '-c', 'user.name=Skill Verification', '-c', 'user.email=skill-verification@example.invalid', 'commit', '-qm', 'fixture baseline')
    rules = fixture / '.gitignore'
    rules.write_text('_*.py\n*.log\ndata/raw/\n')
    harmed = ['src/package/__init__.py', 'src/_helpers.py', 'docs/audit/run.log', 'data/raw/README.md']
    for name in harmed:
        assert git(fixture, 'check-ignore', '-v', '--', name).stdout
    rules.write_text('/scratch/\n/runs/local-debug/*.log\n__pycache__/\n/.venv/\n')
    retained = harmed + ['scripts/analyze.py']
    for name in retained:
        assert not git(fixture, 'check-ignore', '--no-index', '-v', '--', name, allowed=(1,)).stdout
    ignored = ['scratch/cache.tmp', 'runs/local-debug/debug.log', '__pycache__/a.pyc', '.venv/pyvenv.cfg']
    for name in ignored:
        assert git(fixture, 'check-ignore', '-v', '--', name).stdout
    assert git(fixture, 'ls-files', '--', 'scratch/tracked.tmp').stdout.strip() == 'scratch/tracked.tmp'
    assert not git(fixture, 'check-ignore', '-v', '--', 'scratch/tracked.tmp', allowed=(1,)).stdout
    assert git(fixture, 'check-ignore', '--no-index', '-v', '--', 'scratch/tracked.tmp').stdout
    (fixture / 'user.txt').write_text('user staged work\n')
    git(fixture, 'add', '--', 'user.txt')
    (fixture / 'scripts/analyze.py').write_text('print(2)\n')
    (fixture / 'docs/new-note.md').write_text('task untracked document\n')
    index_before = git(fixture, 'ls-files', '--stage').stdout
    staged_before = git(fixture, 'diff', '--cached', '--binary').stdout
    observed = {label: git(fixture, *args).stdout for label, args in {
        'status': ('status', '--short'), 'unstaged': ('diff', '--name-only'), 'staged': ('diff', '--cached', '--name-only'), 'untracked': ('ls-files', '--others', '--exclude-standard')}.items()}
    assert observed['staged'].strip() == 'user.txt'
    assert observed['unstaged'].strip() == 'scripts/analyze.py'
    assert 'docs/new-note.md' in observed['untracked']
    assert git(fixture, 'ls-files', '--stage').stdout == index_before
    assert git(fixture, 'diff', '--cached', '--binary').stdout == staged_before
    print(json.dumps({'git_fixture': 'PASS', 'legacy_false_exclusions': len(harmed), 'narrow_rules_retained': len(retained), 'narrow_rules_ignored': len(ignored), 'tracked_file_retained': True, 'original_staged_diff_unchanged_by_read_only_checks': True}, ensure_ascii=False))
old_size = len(git(root, 'show', base + ':SKILL.md').stdout.encode('utf-8')) if base_available else 22841
new = (root / 'SKILL.md').read_bytes()
print(json.dumps({'core_bytes_before': old_size, 'core_bytes_after': len(new), 'core_reduction_percent': round((1-len(new)/old_size)*100, 1), 'skill_sha256': hashlib.sha256(new).hexdigest()}))
