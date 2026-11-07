#!/usr/bin/env bash
# 高品質レンダリング一式 (Cycles / CPU)。前提: bpy モジュール入りの Python (例: uv venv --python 3.11 && uv pip install bpy pillow)
PY=${PY:-/tmp/bl/.venv/bin/python}; cd "$(dirname "$0")/.."
R="$PY -W ignore blender/build_imac_pc_v8.py"; OUT=render/blender
mkdir -p $OUT
$R --view front   --color silver --res 1920x1080 --samples 128 --out $OUT/front_silver.png --save-blend blender/imac_pc.blend --export viewer/imac_pc.glb
$R --view front   --color blue   --tilt 8 --res 1920x1080 --samples 128 --out $OUT/front_blue_tilt.png
$R --view back    --color orange --res 1920x1080 --samples 128 --out $OUT/back_orange.png
$R --view side    --color green  --tilt 12 --res 1920x1080 --samples 128 --out $OUT/side_green.png
$R --view inside  --color pink   --cut --res 1920x1080 --samples 160 --out $OUT/inside.png
$R --view closeup --color silver --cut --res 1920x1080 --samples 160 --out $OUT/board_closeup.png
$R --view io      --color silver --res 1920x1080 --samples 128 --out $OUT/io_panel.png
$R --view explode --color purple --explode 1 --res 1920x1080 --samples 128 --out $OUT/exploded.png
for c in silver blue purple pink orange yellow green; do $R --view front --color $c --res 1280x720 --samples 64 --out $OUT/lineup_$c.png; done
gzip -9 -c viewer/imac_pc.glb | base64 -w0 > viewer/imac_pc.glb.txt      # gzip+base64(実穴で容量が増えるため。ビューアが DecompressionStream で展開)
echo ALLDONE
