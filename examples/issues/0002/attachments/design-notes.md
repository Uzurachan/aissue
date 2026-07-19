# ダークモード配色案(ドラフト)

## カラートークン案

| トークン           | ライト    | ダーク    |
|--------------------|-----------|-----------|
| background/primary | #FFFFFF   | #121212   |
| background/surface | #F5F5F5   | #1E1E1E   |
| text/primary       | #1A1A1A   | #EDEDED   |
| text/secondary     | #5C5C5C   | #A0A0A0   |
| accent             | #2563EB   | #3B82F6   |

## 適用方針

- CSS変数(`--color-*`)でトークン化し、`data-theme="dark"` 属性の有無で切り替える
- 画像・アイコン類はダークモード時に明度を落とした専用アセットを用意するか検討中
- コントラスト比はWCAG AA(4.5:1以上)を満たすことを確認済み
