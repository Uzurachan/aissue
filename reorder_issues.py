#!/usr/bin/env python3
"""Issueの「やる順番」(order)を設定するヘルパースクリプト。

frontmatterの `order` フィールドを書き換える。`list_issues.py` はこの値をもとに
並べ替えて表示する。順番の意味づけ(何を優先すべきか)はAI/人間の判断に委ね、
このスクリプトは値の書き込みに徹する。

使い方1: 複数Issueをまとめてこの順にしたい場合
    python3 reorder_issues.py --sequence 0003,0001,0002
    (0003→order=1, 0001→order=2, 0002→order=3 が設定される)

使い方2: 1件だけ順番を調整したい場合
    python3 reorder_issues.py --id 0001 --order 1
"""

import argparse
import os

from aissue_common import FRONTMATTER_DELIMITER, load_config, replace_field, split_frontmatter


def write_order(issues_dir, issue_id, order):
    issue_dir = os.path.join(issues_dir, issue_id)
    index_path = os.path.join(issue_dir, "index.md")
    if not os.path.isfile(index_path):
        raise SystemExit(f"Issueが見つかりません: {index_path}")

    with open(index_path, "r", encoding="utf-8") as f:
        text = f.read()

    frontmatter, rest = split_frontmatter(text)
    frontmatter = replace_field(frontmatter, "order", str(order))
    new_text = f"{FRONTMATTER_DELIMITER}\n{frontmatter}\n{FRONTMATTER_DELIMITER}{rest}"

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_text)

    print(f"{index_path}: order = {order}")


def main():
    parser = argparse.ArgumentParser(description="Issueのやる順番(order)を設定する")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--sequence",
        help="カンマ区切りのIssue ID。この順に1から連番でorderを設定する(例: 0003,0001,0002)",
    )
    group.add_argument("--id", help="1件だけorderを設定する対象のIssue ID")
    parser.add_argument("--order", type=int, help="--id 指定時に設定するorder値")
    args = parser.parse_args()

    config = load_config()

    if args.sequence:
        ids = [x.strip() for x in args.sequence.split(",") if x.strip()]
        for i, issue_id in enumerate(ids, start=1):
            write_order(config["issues_dir"], issue_id, i)
    else:
        if args.order is None:
            parser.error("--id を使う場合は --order も指定してください")
        write_order(config["issues_dir"], args.id, args.order)


if __name__ == "__main__":
    main()
