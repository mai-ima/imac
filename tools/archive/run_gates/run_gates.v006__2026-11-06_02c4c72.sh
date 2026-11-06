#!/bin/bash
# 品質ゲート一括実行(失敗を隠さない)。順序: 正規データ→計算→独立検証→台帳
cd "$(dirname "$0")/.."
rc=0; unv=0
for c in "python3 tools/stale_check.py" "python3 tools/fitcheck.py" "python3 tools/cablemodel.py" "python3 tools/cable_check.py" "python3 tools/stability.py" "python3 tools/motion_check.py" "python3 tools/balance_calc.py" "python3 tools/swivel_calc.py" "python3 tools/power_budget.py" "python3 tools/dfm_check.py" "python3 tools/strength_check.py" "python3 tools/fit_tolerance.py" "python3 tools/audit_manifest.py"; do
  echo "=== $c"; out=$($c 2>&1); r=$?; echo "$out" | tail -6; echo "exit=$r"; if [ $r -eq 2 ]; then echo "  → UNVERIFIED(合格ではない)"; unv=$((unv+1)); elif [ $r -ne 0 ]; then rc=1; fi
done
echo "UNVERIFIEDゲート: $unv 件"; exit $rc
