#!/usr/bin/env bash
# git フックを版管理下(tools/githooks)に切り替える。新しい作業環境/クローンでは最初に1回実行する(CLAUDE.md参照)。
cd "$(git rev-parse --show-toplevel)" && git config core.hooksPath tools/githooks && echo "core.hooksPath=tools/githooks"
