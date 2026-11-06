# iMac風 一体型ゲーミングPC 設計書 (v4: 全て市販品/外装のみ特注)

- 目標: 現行最新iMac(M6, 249,800円〜)と同等以下の価格で、同等以上の性能+ゲーム可+拡張性。外観はiMac風、**内部は全て市販品**。
- 決定事項: 27型4K(BOE MV270QUM-N50)。本体 620×415.3mm、前面スラブ18mm、背面ドーム込み総厚190mm(spec.json)。
- 部品・寸法・根拠・実現性の検証は **`docs/bom-final.md`**(BOMと未確認一覧)、iMac調査は `docs/research-notes.md` / `docs/anatomy.md`、モデルの構成は `docs/build-guide.md`。
- 実現性チェック: `python3 tools/fitcheck.py`(結果: `docs/fitcheck-report.txt`)。

## 概算予算 (要: 最新価格確認。確認できた価格以外は想定)
上限 249,800円。確認できたのはGPU約5.2万円(発売時)、CPU約4.2万円(2025年)、マザー約2.8〜3.9万円のみ。27型4Kパネル+制御基板、Flex ATX電源、ファン、板金外注の価格は未確認のため、**合計は上限を超える可能性が高い**。削減案: 安価なB650I系ボード、Ryzen 5 7600、板金の簡素化。

## 外観
iMac公式画像の実測に基づく7色(`model/spec.json`)。白縁の一枚ガラス前面、色付きチン、背面左下の縦スロット4つ、一枚板スタンド。ポッドは背面メッシュ吸気+上下スリット(実形状の穴)。

## 成果物
- `blender/build_imac_pc.py`: Blender(Cycles)モデル。実在部品を `model/parts.json`/`layout.json` から配置。`blender/render_all.sh` で高画質レンダリング一式。
- `viewer/index.html` + `viewer/imac_pc.glb`: Three.jsビューア(上記GLBを読み込み)。
- `cad/imac_like_pc.scad`: OpenSCADの簡易寸法確認用(旧設計。27型・実在部品の反映は未了)。
