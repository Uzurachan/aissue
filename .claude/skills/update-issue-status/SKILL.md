---
name: update-issue-status
description: このリポジトリ(Pearssue)でユーザーが「Issue XXXXをdoneにして」「イシューXXXXを完了にして」「あれ保留にして」「完了にした」「対応中にして」のように既存Issueのステータス変更を依頼したときに使う。「Issue」「issue」「イシュー」いずれの表記でも発火する。対象Issueを特定し `update_status.py` を呼び出して `index.md` のfrontmatterを更新する。
---

# Issueステータス更新

Pearssueのステータス値は `new` / `processing` / `pending` / `done` の4つ(lowercase-kebab)。定義は `AGENTS.md` を参照。

- `new`: 起票直後で未着手
- `processing`: 対応中
- `pending`: 一時中断・保留(返答待ちや外部要因)
- `done`: 完了

**状態遷移に制限はない。** どの状態からどの状態へも自由に変更してよい。

## 対象Issueの特定

- ユーザーがIssue ID(例: `0001`)を明示していればそれを使う。
- IDが分からない場合は `issues/*/index.md` のtitleやtagsから該当しそうなものを探す。
- 複数候補があり一意に絞れない場合は、ユーザーに確認する。

## ステータスの決定

- ユーザーの発言からstatusを判断する(例:「終わった」「直した」→`done`、「保留」「様子見」「返答待ち」→`pending`、「着手した」「対応中」→`processing`、「差し戻し」「やり直し」→`new`や`processing`など文脈で判断)。
- 曖昧な場合はユーザーに確認する。

## 更新の実行

```sh
python3 update_status.py --id <issue_id> --status <status>
```

保留・差し戻しなど理由を残す価値がある変更では `--note` を付け、本文末尾に変更メモとして追記する:

```sh
python3 update_status.py --id <issue_id> --status pending --note "<変更理由>"
```

- frontmatterの `status` と `updated` は `update_status.py` が自動で書き換える。既存のfrontmatterやattachments/本文には影響しない。
- 実行後、標準出力に表示される `index.md` のパスと変更内容をユーザーに報告する。

## 注意点

- frontmatterの書き換えは必ず `update_status.py` を通して行う(手でファイルを編集しない)。クォートの有無や日本語混じりのタイトルなどでも安全に扱える。
- 状態遷移のバリデーションは行わない設計のため、この Skill 側でも「その遷移は禁止」といった判断はしない。
