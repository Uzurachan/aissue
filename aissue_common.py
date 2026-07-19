"""aissueの各スクリプトで共有する設定読み込み・frontmatter操作ユーティリティ。"""

import json
import os
import re

CONFIG_PATH = ".aissue.json"

DEFAULT_CONFIG = {
    "id_format": "sequential",
    "issues_dir": "issues",
    "attachments_dir": "attachments",
}

FRONTMATTER_DELIMITER = "---"


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    return {**DEFAULT_CONFIG, **config}


def yaml_str(value):
    """PythonのstrをYAML(frontmatter)上で安全なクォート付き文字列にする。"""
    return json.dumps(value, ensure_ascii=False)


def split_frontmatter(text):
    """index.mdのテキストを (frontmatter文字列, 残りの本文) に分割する。"""
    prefix = f"{FRONTMATTER_DELIMITER}\n"
    if not text.startswith(prefix):
        raise ValueError("index.md にfrontmatterが見つかりません")
    end = text.index(f"\n{FRONTMATTER_DELIMITER}", len(prefix))
    frontmatter = text[len(prefix):end]
    rest = text[end + len(f"\n{FRONTMATTER_DELIMITER}"):]
    return frontmatter, rest


def replace_field(frontmatter, field, raw_value):
    """frontmatter文字列内の `field: ...` 行を書き換える(なければ末尾に追加する)。"""
    pattern = re.compile(rf"^{field}:.*$", re.MULTILINE)
    line = f"{field}: {raw_value}"
    if pattern.search(frontmatter):
        return pattern.sub(line, frontmatter, count=1)
    return frontmatter + f"\n{line}"


def _yaml_unquote(value):
    value = value.strip()
    if value == "[]":
        return []
    if value == "null" or value == "":
        return None
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    try:
        return int(value)
    except ValueError:
        return value


def parse_frontmatter(frontmatter):
    """frontmatter文字列(区切り線を除いた中身)を簡易的にdictへパースする。

    独自のIssueスキーマ(トップレベルのkey: valueと、配列の`- item`)だけを
    扱えれば十分なため、汎用YAMLパーサーは実装しない。
    """
    data = {}
    lines = frontmatter.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            items = []
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("- "):
                items.append(_yaml_unquote(lines[j].strip()[2:]))
                j += 1
            data[key] = items
            i = j
            continue
        data[key] = _yaml_unquote(value)
        i += 1
    return data


def read_issue(index_path):
    """index.mdを読み、frontmatterをdictとして返す。"""
    with open(index_path, "r", encoding="utf-8") as f:
        text = f.read()
    frontmatter, _ = split_frontmatter(text)
    return parse_frontmatter(frontmatter)
