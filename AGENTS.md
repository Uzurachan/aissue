# AGENTS.md

## プロジェクト概要

**aissue** は、人間にもAIエージェントにも可読性があるIssue管理ツール。
AIがタスクの読み取り・更新・管理を主体的に行えることを前提に設計する。

## コンセプト

- **人間可読 = AI可読**: 特別なパーサーがなくても人が目視で読め、同時にAIがそのまま構造を理解できるフォーマットを採用する。プレーンテキスト/Markdownベースを基本方針とし、独自バイナリ形式や複雑なDBスキーマへの依存は避ける。
- **AIがファーストクラスの操作主体**: 閲覧だけでなく、Issueの作成・更新・クローズ・優先度付けなどをAIエージェントが自律的に行える設計にする。人間用UIはAIの操作を邪魔しない形で後付けできるようにする。
- **Gitとの親和性**: Issueの変更履歴はGitの差分として自然に追えることを重視する(可能な限り)。

## 設計方針(現時点で確定していること)

- **保存形式はファイルベース(Markdown + frontmatter)に決定。**
  - **1 Issue = 1ディレクトリ**とする(例: `issues/0001/`)。ディレクトリ名は0埋め4桁の連番IDのみとし、タイトル変更時にディレクトリ名のリネームが発生しないようにする。
  - ディレクトリ直下に `index.md` を置き、Issue本体(frontmatter + 本文)を記載する。
  - 添付ファイル(ログ・設計メモ・スクリーンショット等)は同ディレクトリ内の `attachments/` 配下に格納する。添付は任意(なくてもよい)。
  - メタデータ(id, title, status, priority, tags, assignee, order, created, updatedなど)は `index.md` のYAML frontmatterに記載し、本文はMarkdownの自由記述とする。
  - DBサーバーやバイナリ形式には依存しない。リポジトリをcloneするだけで全Issueが人にもAIにもそのまま読める状態を保つ。
  - Gitの差分でIssueの変更履歴が自然に追える(コミット単位でIssueの追加・更新・クローズが追跡可能)ことをメリットとして活かす。
  - 実例は `examples/issues/` を参照(`0001/`はバグ報告+ログ添付の例、`0002/`は機能要望+設計メモ添付の例)。
- **実装言語はPythonに決定。** 外部ライブラリに依存せず標準ライブラリのみで実装する方針(セットアップの敷居を下げるため)。
- **初回セットアップスクリプト `init.py` を用意。** 対話式でIssue IDの形式(連番 / 日付+連番 / ULID)、Issue格納ディレクトリ名、添付ファイル用サブディレクトリ名を決め、設定を `.aissue.json` に書き出す。詳細は `README.md` の「セットアップ」を参照。
- **Issue作成は「対話(AI/Skill)+ ファイル生成(スクリプト)」の役割分担に決定。**
  - ヒアリングや本文の組み立てはAIエージェント(Claude Codeでは `.claude/skills/create-issue/SKILL.md`)が担当する。ユーザーが「Issueを作って」のように自然言語で依頼した際に発火する想定。
  - ID採番・ディレクトリ作成・frontmatter生成といった機械的な処理は `new_issue.py` に一本化し、AIの解釈揺れによるID重複やフォーマット崩れを防ぐ。
  - `new_issue.py` は `.aissue.json` の `id_format` に従い次のIDを採番し、`<issues_dir>/<id>/index.md` と `<issues_dir>/<id>/<attachments_dir>/` を生成する(本文は標準入力または `--body-file` で受け取る)。
- **ステータス値は `new` / `processing` / `pending` / `done` の4つに決定。** 表記はlowercase-kebabで統一する。
  - `new`: 起票直後でまだ着手していない
  - `processing`: 対応中
  - `pending`: 一時中断・保留(他者の返答待ちや外部要因などで進行が止まっている状態)
  - `done`: 完了
  - **状態遷移に制限は設けない。** どのステータスからどのステータスへも自由に変更可能とし、ツール側でのバリデーションは行わない(AI/人間の判断を尊重する)。
  - ステータス更新も作成と同様に「対話(AI/Skill)+ ファイル更新(スクリプト)」の役割分担とする。Claude Codeでは `.claude/skills/update-issue-status/SKILL.md` が対象Issueの特定とstatus判断を担当し、実際のfrontmatter書き換えは `update_status.py` に一本化する(`--note` で変更理由を本文末尾に追記可能)。
- **一覧表示・優先順位付けのため `order` フィールドを追加。**
  - `order` は「やる順番」を表す整数(小さいほど先)。未設定は `null`(新規作成直後のデフォルト)で、一覧では末尾かつ `-` 表示になる。
  - 表示は `list_issues.py` に一本化(デフォルトで`order`昇順表示、`--sort priority|created|id`や`--status`での絞り込みに対応)。出力は人間向けの整形済みテーブルのみ(JSON出力は現状用意しない)。
  - 並べ替えは `reorder_issues.py` に一本化。`--sequence id1,id2,...` で複数Issueをまとめてこの順に採番するか、`--id <id> --order <n>` で1件だけ調整する。`order`の重複解消(自動リナンバリング)は行わず、同順位は許容してid順で安定表示する。
  - Claude Codeでは `.claude/skills/list-issues/SKILL.md` が「一覧見せて」「Aを先にやって」のような自然言語をヒアリングし、`list_issues.py` / `reorder_issues.py` を呼び出す。
- 今後の実装は、上記コンセプトを満たすかどうかを判断基準にする。
- 大きな設計判断をする際は、目的・前提・範囲・長期的な影響を一段引いて見直すこと。

## 今後決めるべきこと(TBD)

- frontmatterのスキーマの正式確定(必須フィールド/任意フィールドの切り分け、`examples/`の項目はあくまで叩き台)
- インターフェース(CLI / TUI / Web UI / API)。現状はSkill経由のIssue作成・ステータス更新・一覧表示/並べ替えのみ
- Issue間の関連付け(親子・依存関係)の表現方法
- 複数人(複数AI)での同時編集・競合解決の方針(Git管理下での衝突時の扱い)
- `order`の重複が増えてきた場合の自動リナンバリングの要否

## リポジトリ構成

- `README.md`: プロジェクトの簡易説明・セットアップ手順
- `LICENSE`: MIT License
- `init.py`: 初回セットアップ用の対話式スクリプト(Python標準ライブラリのみ使用)
- `aissue_common.py`: 設定読み込み・YAML文字列化・frontmatterの分割/パース/書き換えなど、各スクリプトで共有するユーティリティ
- `new_issue.py`: Issueを1件新規作成するヘルパースクリプト(ID採番・ファイル生成を担当)
- `update_status.py`: 既存Issueのstatus/updatedを書き換えるヘルパースクリプト
- `reorder_issues.py`: 既存Issueのorder(やる順番)を書き換えるヘルパースクリプト
- `list_issues.py`: Issue一覧をテーブル表示するスクリプト(ソート・statusフィルタ対応)
- `.claude/skills/create-issue/SKILL.md`: Claude Code向けのIssue作成Skill。自然言語での依頼をヒアリングし `new_issue.py` を呼び出す
- `.claude/skills/update-issue-status/SKILL.md`: Claude Code向けのステータス更新Skill。対象Issueとstatusを判断し `update_status.py` を呼び出す
- `.claude/skills/list-issues/SKILL.md`: Claude Code向けの一覧表示・並べ替えSkill。`list_issues.py`/`reorder_issues.py`を呼び出す
- `examples/issues/`: Issueディレクトリ構成のサンプル(`0001/`, `0002/`など)
- `.aissue.json`: `init.py` 実行後に生成される設定ファイル(id_format, issues_dir, attachments_dir)

## コーディング規約

- Python標準ライブラリのみを使用し、外部パッケージへの依存を追加しない(現時点の方針)。
- スクリプトは対話的な実行(`python3 init.py` など)を前提にシンプルに保ち、過度な抽象化・オプション追加は避ける。
- 複数スクリプトで使う設定読み込み・frontmatter操作等のロジックは `aissue_common.py` に集約し、重複させない。
