# 3Dモデルの構成と移行方法

## 構成(単一の出所 → 各ツール)
```
model/spec.json   (外形・色)
model/parts.json  (実在部品DB: 寸法・根拠・確認状況)
model/layout.json (ポッド内の配置)
   ├─> tools/fitcheck.py            (収まり・干渉・電力・風量の機械チェック)
   └─> blender/build_imac_pc.py ─> Cycles画像 / imac_pc.blend / viewer/imac_pc.glb
                                      └─> viewer/index.html (GLBを読み込むThree.jsビューア)
cad/imac_like_pc.scad は旧設計の簡易版(未更新)
```
- 寸法・色は `model/spec.json`、部品は `parts.json`、配置は `layout.json`。Blender版はこれらを直接読み、ビューアはBlenderが書き出したGLBを読み込むため、**モデルの出所はBlenderに一本化**。
- 座標系は設計図の (x右, y上, z手前)。Blenderでは (x, -z, y) に変換。単位はmm(1 Blender単位=1mm)。

## 実行方法 (Blender 5.0 の bpy モジュール)
```bash
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python bpy pillow
.venv/bin/python blender/build_imac_pc.py --view front --color blue --res 1920x1080 --samples 128 --out render/blender/x.png
#   --view front|back|side|inside|closeup|io|explode|top   --cut(背面カバーなし)  --tilt 8  --explode 1  --panel 24|27
bash blender/render_all.sh      # 一式(約20分/CPU 4コア)
```
Blender本体でも実行可: `blender -b -P blender/build_imac_pc.py -- --view front --out x.png`

## 他ツールへの移行
| 出力 | 用途 |
|---|---|
| `blender/imac_pc.glb` | Three.js / Babylon / Unity / Unreal / Blender 以外のビューア。名前付きノード(`fan_cpu_rotor` など)で個別操作可 |
| `blender/imac_pc.blend` | Blenderで編集。マテリアルはPrincipled BSDF |
| `cad/imac_like_pc.scad` | OpenSCAD → STL(3Dプリント試作・寸法確認) |
| 製造用CAD(STEP) | **未作成**。板金の外注には別途CAD(FreeCAD/CadQuery/Fusion)でSTEP/DXFを起こす必要がある。`spec.json` の寸法を入力にする |

## 制約
- 実在製品(GPU/基板/クーラー)は公開寸法に合わせた再現で、メーカーのCADではない。内部の細かい部品配置は典型例。
- Blender版の背面メッシュ吸気は透過マスク(穴は実形状ではない)、ファン枠・スリットはブール演算の実形状。
