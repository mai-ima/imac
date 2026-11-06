# ケーブル/配管の曲げ・剛性 調査 (2026-11-06, サブエージェント調査。検索要約ベース・一次資料の本文は未確認)
## 結論
公式の最小曲げ半径が取得できたのは少数(RG178/RG316同軸、12V-2x6のコネクタ直後)。他(ATX/EPS/PCIe、ライザー、AIOホース、eDP同軸、FFC)は**UNVERIFIED**で、設計では暫定値(docs/spec/wiring-spec.md, tools/cablemodel.py の mbr)を使い、**実物で確認するまで未確定**とする。
## 確認できた値
| 対象 | 値 | 出典 |
|---|---|---|
| 12V-2x6/12VHPWR(参考: 本機は8ピン使用) | コネクタから約35mm(Corsairは言語版で30〜40mm)は曲げない。装着後は左右方向に曲げない | CableMod/Seasonic/Corsair(wccftech, TechPowerUp) |
| RG178(SMA延長) | 外径約1.8mm: 静的10mm、反復18mm(50回)、動的27mm(Huber+Suhner)。Lapp: 固定6×OD、頻繁10×OD | Huber+Suhner/Lapp/L-com |
| RG316 | 約13〜15mm(L-com) | L-com |
| 同軸の一般則 | 外径の10倍以上(AS50881)、6倍の記載もあり | Lectromec |
| 多対銅ケーブル | 10×OD / 遮蔽付き鉱山ケーブル 6×OD(Wesco) | Lectromec/Wesco |
| FFC/FPC(基板の目安) | 静的: 厚みの約10倍、動的: 100〜200倍(IPC-2223引用、個別品は要データシート) | FLIR/PCBONLINE/JLCPCB |
| eDP極細同軸(I-PEX CABLINE-CA II) | AWG38, 45Ω。最小曲げ半径は公式UNVERIFIED | distyparts datasheet |
| ARCTIC LF III Pro 240ホース | 外径12.4/内径6.0/450mm(小売転載)。**曲げ半径UNVERIFIED** → 外径の6〜10倍=約75〜125mmを暫定採用(推定) | teqex/c2g |
| LINKUP AVA5(AG-P5-33SS-020BK-v2, 直線20cm) | 幅/厚/曲げ半径 UNVERIFIED。レビューで急な曲げは遮蔽に応力痕(60cm品)。**緩いS字まで**を前提 | heise/desertcart/GraphicsCardHub |
| SF750付属 ATX24/EPS/PCIe | 長さ300/400/400mm(Corsair SFキット表記)。AWG/剛性/半径 UNVERIFIED | Corsair CP-8920202 |
## 設計ルール(暫定=推定を含む)
1. 電源ケーブル(スリーブ16〜18AWG)はコネクタ後方に**直線15〜20mm**を確保し、曲げ半径は外径の3〜4倍(ATX24=30mm, EPS/PCIe=20mm)以上(**暫定**)。
2. AIOホースは半径**75mm以上**(6×OD, 暫定)。90°を超える折れ・S字の連続は避け、ポンプ/ラジエーターのコネクタ根元に曲げ荷重をかけない。
3. ライザーは緩いS字まで(半径は問合せ)。ツイスト禁止。
4. 同軸(SMAアンテナ延長 RG178)は静的10mm以上、整備で動かす箇所は27mm以上。
5. eDPアンビリカルは外径の6〜10倍以上、ロックコネクタ根元にストレインリリーフ。
6. すべて「曲げ半径の実物確認」を購入前チェックリストへ(U45)。
## 追加調査(未確認)
LINKUP AVA5実寸と曲げ半径、ARCTICホース曲げ半径、I-PEX/Hirose/JAE公式の最小曲げ半径と挿抜寿命、UL 758/IPC-WHMA-A-620原文、SF750ケーブルの実仕様(フラット/スリーブ/AWG)。
