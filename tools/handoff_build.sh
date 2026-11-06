#!/bin/bash
# 業者提出パッケージを正規順で再生成: JSON → 図面/DXF(gen_mfg_drawings, gen_cad_drawings, gen_mech_sections, gen_service_drawings) → handoff(STEP/BOM/RFQ) → PDF → 機構設計書コピー → SHA256SUMS
cd "$(dirname "$0")/.."; PY=${PY:-/tmp/bl/.venv/bin/python}
for g in gen_mfg_drawings gen_cad_drawings gen_mech_sections gen_service_drawings; do $PY tools/$g.py >/dev/null || { echo "FAIL $g"; exit 1; }; done
$PY tools/gen_handoff.py >/dev/null || exit 1
node tools/svg2pdf.js >/dev/null || exit 1
mkdir -p handoff/05_機構設計書; cp docs/mechanisms/*.md handoff/05_機構設計書/ 2>/dev/null
(cd handoff && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt)
echo "handoff rebuilt: $(wc -l < handoff/SHA256SUMS.txt) files hashed"
