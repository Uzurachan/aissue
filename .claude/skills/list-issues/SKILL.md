---
name: list-issues
description: このリポジトリ(Pearssue)でユーザーが「Issue一覧見せて」「イシュー一覧見せて」「今何がある?」「やる順番教えて」「Aを先にやって」「これを一番にして」「同僚に共有できる形にして」「HTMLで書き出して」のように一覧表示・優先順位の並べ替え・共有用ファイルの出力を依頼したときに使う。「Issue」「issue」「イシュー」いずれの表記でも発火する。`list_issues.py` で一覧表示、`reorder_issues.py` で `order` フィールドを書き換え、`export_html.py` で共有用HTMLファイルを出力する。
---

# Issue一覧・並べ替え

PearssueのIssueは `order`(やる順番、数値。小さいほど先)というfrontmatterフィールドを持つ。未設定は `null` で、一覧では末尾かつ `-` 表示になる。定義は `AGENTS.md` を参照。

## 一覧表示

```sh
python3 list_issues.py
```

- デフォルトは `order` 昇順(未設定は末尾)。
- ソートキーを変えたい場合: `--sort priority` / `--sort created` / `--sort id`
- ステータスで絞りたい場合: `--status processing` のように指定
- 結果はテーブルのまま(整形済み)ユーザーに見せればよい。要約や加工は不要。

## 並べ替え

1. ユーザーの発言から対象Issueを特定する。IDが明示されていなければ `issues/*/index.md` のtitleから該当を探し、複数候補があれば確認する。
2. 「AをBより先に」「この順番で」のように複数件まとめて並べ替えたい場合は `--sequence` を使う。指定した順に1から連番で `order` が設定される(リストに含めなかったIssueの `order` は変更されない):

```sh
python3 reorder_issues.py --sequence <id1>,<id2>,<id3>
```

3. 1件だけ順番を調整したい場合は `--id` と `--order` を使う:

```sh
python3 reorder_issues.py --id <id> --order <n>
```

4. 並べ替え後は `python3 list_issues.py` で結果を再表示し、意図した順序になっているかユーザーと確認する。

## 共有用HTMLファイルの出力

ユーザーが「同僚に共有したい」「ファイルとして渡したい」「HTMLにして」のように言った場合は、テーブル表示ではなく `export_html.py` で単体のHTMLファイルを生成する:

```sh
python3 export_html.py --output issues.html
```

- `list_issues.py` と同じ `--sort` / `--status` オプションが使える。
- 出力される `issues.html` は外部依存のない自己完結ファイルなので、そのままメールやチャットで送ったりファイル共有すればよい。
- 生成後、出力パスをユーザーに伝える(必要ならブラウザで開いて内容を確認してもよい)。

## 注意点

- `order` の重複は許容される(同順位として扱われ、一覧では元のID順で安定的に並ぶ)。厳密な重複解消はしない。
- frontmatterの書き換えは必ず `reorder_issues.py` を通して行う(手でファイルを編集しない)。
