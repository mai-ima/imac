# 3Dモデルの構成と移行方法

## 構成(単一の出所 → 各ツール)
```
model/spec.json ──┬─> blender/build_imac_pc.py  ─> Cycles画像 / imac_pc.blend / imac_pc.glb   (写実レンダリングの本流)
                  ├─> cad/imac_like_pc.scad      (OpenSCAD: 寸法確認・STL出力用の簡易版)
                  └─> viewer/index.html          (Three.js: ブラウザで回転・分解・動作表示)
```
- 寸法・色・部品名は `model/spec.json` に集約。Blender版はこのファイルを直接読む。OpenSCAD/Three.js版は同じ値を定数で持つ(27型: 本体616.7x413.7mm)。
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
