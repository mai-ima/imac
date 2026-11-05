# 配線表(自動生成: tools/gen_package.py)

長さは経路折れ線長×1.15(余長)。PSU付属ケーブル長は小売記載で公式未確認(U08)。

| ID | 名称 | 接続 | AWG | コネクタ | 設計長mm | PSU付属mm | 判定 |
|---|---|---|---|---|---|---|---|
| W1 | ATX 24ピン | PSU modular(24p) → 基板 ATX24 | 18 | 24p (20+4) | 85 | 300 | OK |
| W2 | CPU EPS 8ピン | PSU modular(EPS) → 基板 CPU_12V(8p) | 16 | EPS 4+4 | 293 | 400 | OK |
| W3 | GPU PCIe 6+2ピン | PSU modular(PCIe) → GPU 8ピン | 16 | PCIe 6+2 | 238 | 400 | OK |
| W4 | コントローラ基板 12V | PSU modular(SATA/周辺) → ctrl_board DC入力 | 20 | SATA電源 or 2pin | 169 | - | OK |
| W5 | アンビリカル(eDP 30p/12V/USB) | ctrl_board eDP → パネル背面コネクタ | - | eDP 30p + 12V + USB2 | 85 | - | OK |

## 配線ルール
- 電源線は番号タグ+色。最小曲げ半径: 24p/EPS/PCIe は線外径の6倍以上(約30mm)。
- ホース(ARCTIC, 450mm, OD12.4): 最小曲げ半径は公式未確認(U)。クリップで固定し90°折れを避ける。
- アンビリカルはトレイ上端のコネクタ。取り外し時は保護キャップ。
- ファンはPWM 4pinを基板FAN_HDRへ(ファンハブ使用時はハブ→基板CPU_FAN)。
