#!/usr/bin/env python3
"""既存Issueのステータスを更新するヘルパースクリプト。

`<issues_dir>/<id>/index.md` のfrontmatterにある `status` と `updated` を書き換える。
ステータス値は `new` / `processing` / `pending` / `done` を想定するが、
状態遷移に制限は設けないため任意の文字列を受け付ける(AGENTS.md参照)。
"""

import argparse
import datetime
import os

from pearssue_common import (
    FRONTMATTER_DELIMITER,
    load_config,
    replace_field,
    split_frontmatter,
    yaml_str,
)


def main():
    parser = argparse.ArgumentParser(description="Issueのステータスを更新する")
    parser.add_argument("--id", required=True, help="Issue ID(ディレクトリ名)")
    parser.add_argument("--status", required=True, help="new / processing / pending / done など")
    parser.add_argument(
        "--note", help="変更理由などのメモ。指定すると本文末尾に追記する"
    )
    args = parser.parse_args()

    config = load_config()
    issue_dir = os.path.join(config["issues_dir"], args.id)
    index_path = os.path.join(issue_dir, "index.md")

    if not os.path.isfile(index_path):
        raise SystemExit(f"Issueが見つかりません: {index_path}")

    with open(index_path, "r", encoding="utf-8") as f:
        text = f.read()

    frontmatter, rest = split_frontmatter(text)

    today = datetime.date.today().isoformat()
    frontmatter = replace_field(frontmatter, "status", yaml_str(args.status))
    frontmatter = replace_field(frontmatter, "updated", today)

    if args.note:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        note_section = f"\n## ステータス変更メモ({timestamp})\n\n{args.note}\n"
        rest = rest.rstrip("\n") + "\n" + note_section

    new_text = f"{FRONTMATTER_DELIMITER}\n{frontmatter}\n{FRONTMATTER_DELIMITER}{rest}"

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_text)

    print(index_path)


if __name__ == "__main__":
    main()
