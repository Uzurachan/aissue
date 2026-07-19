#!/usr/bin/env python3
"""Issue一覧を人間向けテーブルとして表示するスクリプト。

デフォルトでは `order`(やる順番)昇順で表示し、orderが未設定のものは末尾に回す。
`order` は `reorder_issues.py` で設定する。
"""

import argparse
import unicodedata

from pearssue_common import collect_issues, issue_sort_key, load_config

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

    issues.sort(key=issue_sort_key(args.sort))

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
