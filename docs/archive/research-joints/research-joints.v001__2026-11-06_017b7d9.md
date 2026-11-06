# 接合部の部品・材料データ調査 (2026-11-05, 検索スニペット由来 → 全て一次データシートで要原典確認)

出典URLは各行。UNVERIFIED=未確認。設計への反映は docs/joint-analysis.md / docs/failure-analysis.md。

## 1. 締結部品
- PEM TSO/TSOA/TSOS(アルミ用TSOA)スタンドオフ: 板厚0.63mm〜対応、母材硬度上限HRB50/HB82(A5052-H32≈60HBで適合見込み)。t2.0は最小板厚を十分上回る。TSOA-M3-400/800/1200の存在確認。押抜き/トルクアウト値(t2.0)は UNVERIFIED(PEM技術部へ問合せ)。側荷重でクリンチ部破損の注意。 [PEM Standoff Tech Sheet](https://www.pemnet.com/wp-content/uploads/sites/2/2022/06/Standoff_Tech_Sheet.pdf), [TSOA-M3-800](https://devaws.pemnet.com/de/products/product-finder/tsoa-m3-800/)
- M3 Torx拘束ねじ: Essentra(303/316SUS, 10/16/40mm, ねじ掛かり2.0mm表記品あり, Eクリップ記載なし) [Essentra](https://www.essentracomponents.com/en-gb/p/captive-screws-button-head)、Accu(Torxノブ型) [Accu](https://accu-components.com/us/shop/precision-components/precision-screws/captive-panel-screws/metric-torx-knob-captive-panel-screws)。Southco ATCAはPhillipsでTorxではない。T10+Eクリップ品の品番とトルク上限は UNVERIFIED → **拘束ねじは「皿頭+ねじ山抜け止め(Eクリップ)」ではなく、板に圧入するキャプティブ品(Essentra等)へ設計変更を検討**。
## 2. 磁石
- N52 φ8×3の吸着力データは UNVERIFIED。参考: RS Eclipse 8×3(N35)=1.32kgf。K&JのN52 φ9.52×1.59は鋼板1枚2.62lb/両面鋼板10.65lbと試験条件で約4倍違う → 仕様は条件付きで確認。 [RS](https://uk.rs-online.com/web/p/neodymium-magnets/8734966), [K&J](https://www.kjmagnetics.com/d61-n52-neodymium-disc-magnet)
## 3. EMIガスケット(ファブリックオーバーフォーム)
- Parker Chomerics SOFT-SHIELD 3500: >100dB、**閉合力 <1 lb/inch(≈0.175 N/mm)**、圧縮永久歪み15%。 [Parker 3500](https://ph.parker.com/us/en/soft-shield-3500-plated-fabric-wrapped-foam)
- SOFT-SHIELD 3700(シリコーンフォーム): >100dB(100MHz–3GHz)、永久歪み<10%。 [Parker 3700](https://ph.parker.com/gb/en/37-131-1025-09600)
- SOFT-SHIELD 4800: 平均95dB(20MHz–10GHz)。 [4800](https://marianinc.com/wp-content/uploads/2025/08/Chomerics-SOFT-SHIELD-4800.pdf)
- Laird FoF: 1GHzで113dB、表面抵抗<0.07Ω/sq、圧縮30〜75%、永久歪み<20%。 [Mouser](https://www.mouser.jp/laird-fof-emi-shield-gaskets)
- Kitagawa/Tatsuta: UNVERIFIED。**→ 実在値「<1 lb/in ≈ 0.175N/mm」を joint_calc の閉合力計算に採用(外周約1900mmで最大約330N)。磁石12個では不足 → ラッチ増設が必要**。
## 4. ショルダーねじ
- Misumi: 軸径4〜20mm、公差g6/h7/e9。M3.5/M4の具体品番とせん断強度は UNVERIFIED。流通品の例: 肩径5mm M4で公差0/-0.025mm(Zoro)、McMaster M3ねじ肩径5mm頭径9mm頭高4mm。 [Misumi](https://pt.misumi-ec.com/vona2/detail/110300249320/?CAD=01), [McMaster](https://mcmaster.com/products/made-to-order-shoulder-screws)
- → 設計案の「M3.5肩ネジ・肩径4」は規格品に無い可能性。**M3ねじ・肩径5mm(McMaster系)またはMisumi肩径4/5mm品へ見直し**(キーホールの寸法を図面で更新)。
## 5. A5052-H32と陽極酸化
- 降伏≈193MPa(典型。規格最小は130MPa → 設計は最小値)、引張≈228–230MPa、疲労≈117–120MPa(5×10^8回)、伸び≈12%、硬度≈60HB。 [Aerospace Metals](https://www.aerospacemetals.com/wp-content/uploads/2023/06/Aluminum-5052-H32.pdf), [MakeItFrom](https://makeitfrom.com/material-properties/5052-H32-Aluminum)
- 陽極酸化皮膜は絶縁。接地部はマスクまたは導電処理(MIL-DTL-5541 Class 3相当)。ねじ穴内の皮膜でクリアランスが減る事例あり。 [anodizing.org](https://www.anodizing.org/page/military-spec-anodic-coatings), [finishing.com](https://finishing.com/599/69.shtml)
## 6. ガルバニック
- アノード指数: SUS18-8≈0.5–0.6V、Al≈0.9V(差0.3–0.4V、裸金属値)。許容差の目安0.15〜0.25V。接地のため皮膜を除去した箇所は裸Al×SUSとなり湿度で腐食の可能性(一般論)。 [Fastener Superstore](https://fastenersuperstore.com/blog/understanding-preventing-galvanic-corrosion), [Carr Lane](https://www.carrlane.com/engineering-resources/technical-information/galvanic-corrosion/design-considerations-for-galvanic-corrosion)

## 要確定(追加調査リスト → docs/unverified-tracker.md U25〜)
PEMクリンチ部押抜/トルク値(t2.0)、N52 8×3吸着力、拘束ねじ品番とトルク、ショルダーねじ品番・せん断強度、Kitagawa/Tatsuta、皮膜厚と接触抵抗。
