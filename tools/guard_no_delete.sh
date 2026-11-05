#!/usr/bin/env bash
# 過去の仕様書・設計図・図面・モデルの削除を禁止するガード(pre-commitフックから呼ぶ)。
# 対象: docs/ concept/ drawings/ model/ cad/ blender/*.py archive/ の削除。置き換える場合は archive/ に旧版を残してから行う。
deleted=$(git diff --cached --name-status --diff-filter=D | awk '{print $2}' | grep -E '^(docs|concept|drawings|model|cad|archive|render)/|(^|/)archive/|^blender/.*\.(py|sh)$' || true)
if [ -n "$deleted" ]; then
  echo "ERROR: 過去の仕様書/設計図/モデルの削除が含まれています(削除禁止):" >&2; echo "$deleted" >&2
  echo "  旧版を archive/ に保存したうえで、必要なら git rm の代わりに更新してください。復元: git restore --staged --worktree <パス>" >&2; exit 1
fi
