---
name: create-issue
description: このリポジトリ(Pearssue)でユーザーが「Issueを作って」「イシューを作って」「バグ報告したい」「タスクを登録して」「機能要望を追加して」のように新規Issue作成を依頼したときに使う。「Issue」「issue」「イシュー」いずれの表記でも発火する。対話でヒアリングした内容をもとに `new_issue.py` を呼び出し、`issues/<id>/index.md`(と必要なら添付ファイル)を生成する。
---

# Issue作成

Pearssueは人間にもAIにも可読なMarkdownベースのIssue管理ツール。設計方針・frontmatterスキーマの原典は `AGENTS.md` を参照。このSkillは、ユーザーとの対話でIssue内容を詰め、実際のファイル生成は `new_issue.py` に任せることでID採番ミスやフォーマット崩れを防ぐ。

## 前提確認

1. リポジトリ直下に `.pearssue.json` があるか確認する。なければ `python3 init.py` を先に実行するようユーザーに提案する(初回セットアップが未実施のため)。

## ヒアリング

ユーザーの発言だけで足りない項目があれば質問する。既に発言に含まれている情報は聞き直さない。

- **title(必須)**: Issueのタイトル
- **本文**: 概要・背景・詳細。種別に応じて構成を変えてよい
  - バグ報告なら: 概要 / 再現手順 / 期待される動作 / 実際の動作
  - 機能要望なら: 概要 / 背景 / 提案する仕様
  - 上記に当てはまらない場合は自由な構成でよい(概要は必須)
- **status**: 新規作成時は基本的に `new`(着手済みであれば `processing` でもよい)
- **priority**: デフォルト `medium`(`low` / `medium` / `high` などユーザーの意図から判断、迷ったら聞く)
- **tags**: 種別(bug / feature / task等)や関連領域(frontend等)。カンマ区切りで複数可
- **assignee**: 指定がなければ `unassigned`
- **添付ファイル**: ログ・スクリーンショット・設計メモなど、ユーザーが提供・言及したものがあれば添付する

全項目を機械的に質問攻めにしない。自然な会話の中で埋まらない必須項目(主にtitleと本文の概要)だけ確認すれば十分。

## Issueの作成

1. ヒアリングした本文Markdownを一時ファイルに書き出す(スクラッチディレクトリを使う)。
2. 以下のようにヘルパースクリプトを実行する:

```sh
python3 new_issue.py \
  --title "<タイトル>" \
  --status <status> \
  --priority <priority> \
  --tags "<tag1,tag2>" \
  --assignee "<assignee>" \
  --body-file <一時ファイルのパス>
```

3. 標準出力に表示される作成された `index.md` のパスを確認する。
4. 添付ファイルがある場合は、そのIssueディレクトリ内の `attachments/`(`.pearssue.json` の `attachments_dir` で設定されたディレクトリ名)にファイルを配置する。
5. 作成したIssueのパスと内容の要約をユーザーに報告する。

## 注意点

- Issue ID・ディレクトリ作成・frontmatter生成は必ず `new_issue.py` を通して行う(手でファイルを作らない)。IDの採番方式は `.pearssue.json` の `id_format` に従う。
- titleや本文に日本語・記号(コロンなど)が含まれても `new_issue.py` 側でYAML的に安全な形にエスケープされるため、そのまま渡してよい。
