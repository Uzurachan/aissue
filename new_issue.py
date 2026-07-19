#!/usr/bin/env python3
"""Issueを1件新規作成するヘルパースクリプト。

`.pearssue.json` の設定(id_format, issues_dir, attachments_dir)に従って
次のIssue IDを採番し、`<issues_dir>/<id>/index.md` と
`<issues_dir>/<id>/<attachments_dir>/` を生成する。

対話でのヒアリング(タイトルや本文の内容を詰めること)はAI側(Skill)が担当し、
このスクリプトは決まった内容からファイルを機械的に組み立てる役割に徹する。
"""

import argparse
import datetime
import os
import random
import sys

from pearssue_common import load_config, yaml_str

_CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def existing_ids(issues_dir):
    if not os.path.isdir(issues_dir):
        return []
    return [
        name
        for name in os.listdir(issues_dir)
        if os.path.isdir(os.path.join(issues_dir, name))
    ]


def next_sequential_id(issues_dir):
    numbers = [int(name) for name in existing_ids(issues_dir) if name.isdigit()]
    return f"{max(numbers, default=0) + 1:04d}"


def next_date_sequential_id(issues_dir):
    today = datetime.date.today().strftime("%Y%m%d")
    prefix = today + "-"
    numbers = []
    for name in existing_ids(issues_dir):
        if name.startswith(prefix) and name[len(prefix):].isdigit():
            numbers.append(int(name[len(prefix):]))
    return f"{today}-{max(numbers, default=0) + 1:02d}"


def generate_ulid():
    timestamp_ms = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
    randomness = random.getrandbits(80)
    value = (timestamp_ms << 80) | randomness
    chars = []
    for _ in range(26):
        value, remainder = divmod(value, 32)
        chars.append(_CROCKFORD_BASE32[remainder])
    return "".join(reversed(chars))


def next_id(id_format, issues_dir):
    if id_format == "sequential":
        return next_sequential_id(issues_dir)
    if id_format == "date-sequential":
        return next_date_sequential_id(issues_dir)
    if id_format == "ulid":
        return generate_ulid()
    raise ValueError(f"unknown id_format: {id_format}")


def build_frontmatter(issue_id, title, status, priority, tags, assignee, created):
    lines = ["---", f"id: {yaml_str(issue_id)}", f"title: {yaml_str(title)}"]
    lines.append(f"status: {yaml_str(status)}")
    lines.append(f"priority: {yaml_str(priority)}")
    if tags:
        lines.append("tags:")
        lines.extend(f"  - {yaml_str(tag)}" for tag in tags)
    else:
        lines.append("tags: []")
    lines.append(f"assignee: {yaml_str(assignee)}")
    lines.append("order: null")
    lines.append(f"created: {created}")
    lines.append(f"updated: {created}")
    lines.append("---")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="新規Issueを1件作成する")
    parser.add_argument("--title", required=True)
    parser.add_argument("--status", default="new")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--tags", default="", help="カンマ区切り(例: bug,frontend)")
    parser.add_argument("--assignee", default="unassigned")
    parser.add_argument(
        "--body-file",
        help="本文Markdownが書かれたファイルのパス(省略時はstdinから読む)",
    )
    args = parser.parse_args()

    config = load_config()
    issues_dir = config["issues_dir"]
    attachments_dir_name = config["attachments_dir"]

    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()
    else:
        body = sys.stdin.read()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    issue_id = next_id(config["id_format"], issues_dir)
    created = datetime.date.today().isoformat()

    issue_dir = os.path.join(issues_dir, issue_id)
    os.makedirs(issue_dir, exist_ok=False)
    os.makedirs(os.path.join(issue_dir, attachments_dir_name), exist_ok=True)

    frontmatter = build_frontmatter(
        issue_id, args.title, args.status, args.priority, tags, args.assignee, created
    )
    content = f"{frontmatter}\n\n{body.strip()}\n"

    index_path = os.path.join(issue_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(index_path)


if __name__ == "__main__":
    main()
