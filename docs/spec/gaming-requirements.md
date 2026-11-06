# ゲーム性能要件とGPU選定 (2026-11-06, サブエージェント調査。主要レビュー本文(TechPowerUp/Tom's/DF/GN)は取得不可のため暫定)
## 新要件
最新の高負荷ゲーム(Cyberpunk 2077、Call of Duty: Black Ops 7、Cities: Skylines II)を**4Kで快適(平均60fps以上・1% low 45fps以上、DLSS品質可・フレーム生成は別枠)**にプレイできること。
## 調査結果(要旨)
- 公式推奨: Black Ops 7は「Ultra 4K」帯のGPUが RX 9070 XT または RTX 5070。Cities: Skylines IIの公式推奨はi5-12600K/Ryzen 7 5800X+RTX 3080(1080p想定、4K公式要件なし。CPU律速で9950X3Dは十分と推定)。Cyberpunkの4K/RT公式推奨は取得できず。
- 実測/推定(小規模サイト含む、信頼度低): Cyberpunk 4K RTなし ネイティブ: 5070 Ti≈59〜62fps。4K RT(Psycho)ネイティブ: 5070≈30〜45fps → 5070では不足。5080は5070 Tiより約19%速い(KitGuru実測)。パストレーシングは5090でもDLSS Performance+前提(PCGH実測)。Cities SK2 4K Ultra: 5080≈77fps(推定)。
- 判定: **RTX 5070 Ti(16GB)を最小構成**(RTなしは60fps付近、RT/PTはDLSS前提)。5060 Ti 16GBは不足(ASUS Dual 5060 Tiから変更)。5080は余裕だが360W/小型品が長大。
## GPU寸法の制約と決定
- 確認できた小型モデルは PNY Slim(5070 Ti: 290×150×40mm、300W、2スロット / 5080: 300×150×40、360W)。ASUS RTX 5070 EVO Dual(229×120×50, 250W)は5070止まり。NVIDIA SFF-Ready上限: 長さ304×高さ151×厚み50。
- **v8: 寸法基準をPNY RTX 5070 Ti Slim(290×150×40)とする**(具体型番・日本での入手性・価格は購入前に確定: U46)。240mm級の5070 Tiは確認できず → 筐体内の配置を再設計(model/layout.json v8)。
## 電力・熱への影響
GPU TGP 300W+CPU PPT 230W+その他≈81W ≈ DC 636W(AC入力688W) → **電源をSF750→Corsair SF1000(1000W)へ**(使用率64%)。筐体内発熱=AC入力≈688W、排気風量144m³/h(ケースファン廃止、ラジエーターファン2基)でΔT≈13K(目標≤20K)。CPU 83℃推定→**要再計算**(thermal-analysis)。GPU 300Wはプレナム空気を吸うためGPU温度/騒音が最大の懸念。
## 未確認
5060 Ti〜5090の同一条件4Kレビュー(平均/1% low)、Black Ops 7とCyberpunk最新版の4K実測、小型5070 Tiの国内入手性、SF1000の公式仕様。
