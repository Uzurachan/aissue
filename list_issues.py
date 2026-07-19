#!/usr/bin/env python3
"""Issue一覧を人間向けテーブルとして表示するスクリプト。

デフォルトでは `order`(やる順番)昇順で表示し、orderが未設定のものは末尾に回す。
`order` は `reorder_issues.py` で設定する。
"""

import argparse
import os
import unicodedata

from aissue_common import load_config, read_issue

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

HEADERS = ["order", "id", "status", "priority", "title"]


def display_width(text):
    width = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ("F", "W", "A"):
            width += 2
        else:
            width += 1
    return width


def pad(text, width):
    return text + " " * max(0, width - display_width(text))


def collect_issues(issues_dir):
    issues = []
    if not os.path.isdir(issues_dir):
        return issues
    for name in sorted(os.listdir(issues_dir)):
        index_path = os.path.join(issues_dir, name, "index.md")
        if not os.path.isfile(index_path):
            continue
        data = read_issue(index_path)
        data.setdefault("id", name)
        issues.append(data)
    return issues


def sort_key(sort_by):
    def key(issue):
        if sort_by == "order":
            order = issue.get("order")
            return (0, order) if isinstance(order, int) else (1, str(issue.get("id", "")))
        if sort_by == "priority":
            return PRIORITY_ORDER.get(issue.get("priority"), 99)
        if sort_by == "created":
            return issue.get("created") or ""
        return str(issue.get("id", ""))

    return key


def main():
    parser = argparse.ArgumentParser(description="Issue一覧を表示する")
    parser.add_argument(
        "--sort", choices=["order", "priority", "created", "id"], default="order",
        help="並べ替えキー(デフォルト: order)",
    )
    parser.add_argument("--status", help="指定したstatusのIssueのみ表示する")
    args = parser.parse_args()

    config = load_config()
    issues = collect_issues(config["issues_dir"])

    if args.status:
        issues = [i for i in issues if i.get("status") == args.status]

    issues.sort(key=sort_key(args.sort))

    if not issues:
        print("Issueが見つかりません。")
        return

    rows = []
    for issue in issues:
        order = issue.get("order")
        rows.append(
            [
                str(order) if isinstance(order, int) else "-",
                str(issue.get("id", "")),
                str(issue.get("status", "")),
                str(issue.get("priority", "")),
                str(issue.get("title", "")),
            ]
        )

    widths = [display_width(h) for h in HEADERS]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], display_width(cell))

    def format_row(cells):
        return "  ".join(pad(cell, widths[i]) for i, cell in enumerate(cells))

    print(format_row(HEADERS))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(format_row(row))


if __name__ == "__main__":
    main()
