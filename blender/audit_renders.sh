#!/usr/bin/env bash
# 監査用の中解像度レンダリング(約5分)。出力: render/audit/
PY=${PY:-/tmp/bl/.venv/bin/python}; cd "$(dirname "$0")/.."; mkdir -p render/audit
R="$PY -W ignore blender/build_imac_pc.py --res 1280x720 --samples 40"
$R --view front --color silver --out render/audit/a_front.png
$R --view back --color blue --out render/audit/a_back.png
$R --view inside --cut --color silver --out render/audit/a_inside.png
$R --view back --cut --color silver --focus 256,90,25 --dist 330 --az 0 --el 25 --out render/audit/a_gpu.png
$R --view back --cut --color silver --focus 360,85,20 --dist 330 --az 0 --el 25 --out render/audit/a_psu_fan.png
$R --view back --cut --color silver --focus 90,95,25 --dist 330 --az 0 --el 28 --out render/audit/a_board_cooler.png
$R --view back --cut --color silver --focus 555,95,10 --dist 260 --az 0 --el 25 --out render/audit/a_ctrl.png
$R --view back --color silver --focus 0,95,30 --dist 330 --az -75 --el 12 --out render/audit/a_io.png
echo AUDITDONE
