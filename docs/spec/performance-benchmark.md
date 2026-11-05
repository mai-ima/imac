# 性能比較: 現行 iMac (Apple M6) と本PC (2026-11-05 調査, サブエージェント: 報道/集計値ベース)

## 要点(正直な結論)
- 現行iMacは **Apple M6**(apple.com/imac に「powered by the M6 chip」、2026-11-06発売、10/12コアCPU・10/12コアGPU、メモリ最大24/32GB)。M6より新しいiMacチップの公式発表は確認できず(M5 Max搭載iMacは噂)。日本円価格は未確認(U43)。
- **GPU**: RTX 5060 Ti 16GB は M6 内蔵GPUを大きく上回る見込み(Geekbench OpenCL近似で約2.2〜2.4倍。API/版が異なるため近似・信頼度低)。
- **CPU**: Ryzen 7 9800X3D は **M6に対し単発で明確に劣り(GB6 約0.72〜0.74倍, CB2024 約0.60倍)、マルチも同等〜やや劣る(GB6 約0.86倍, CB2024 約0.99倍)**。→ 「CPU・GPUとも iMac を明確に上回る」という要件は **9800X3Dでは満たせない**。9800X3Dの強みはゲーム性能(3D V-Cache)。
## 数値(出典付き; M6は発売前の第三者データベース由来で、iMac実機ではない)
| 指標 | Apple M6 (12C/12G) | 9800X3D | 5060 Ti 16GB |
|---|---|---|---|
| Geekbench 6 単発 | 4,501(〜4,661) [ithinkdiff 2026-09-15] | 約3,336 [HardwareDB] | - |
| Geekbench 6 マルチ | 21,312 [同上] | 約18,346 [HardwareDB] | - |
| Cinebench 2024 単発 | 220 | 132 [Notebookcheck] | - |
| Cinebench 2024 マルチ | 1,368 | 1,358 [Notebookcheck] | - |
| GPU | Metal(GB7) 約92,000 [Notebookcheck 2026-09-19/MacRumors 2026-09-18] | - | GB6.5 Vulkan 138,181 / OpenCL 141,782、Time Spy 約16,000 [Notebookcheck/Wccftech] |
| 4K平均FPS | - | - | UNVERIFIED(Tom's Hardware: 4060 Ti 16GBより約16〜21%速い) |
不確実性: Geekbench Browser一次ページ/TechPowerUpは取得不可(403)。9800X3Dは日付不明の集計値が中心。M6実機レビュー(Notebookcheck/Tom's Hardware)が出たら再確認。
## 設計への影響(要判断)
1. **要件「iMac(M6)以上」を厳密に満たすには CPU の見直しが必要**。x86デスクトップCPUで**単発性能の上回りは現状ほぼ不可能**(M6が単発最上位級)。マルチ性能は上位CPU(例: Ryzen 9 9950X3D 16C/32T)で上回れる可能性があるが、**TDP/PPTが増え(TDP170W/PPT約230W: 要確認 U44)、240mm AIOの余裕と電源余裕(750W)・熱を再計算**する必要がある。
2. 代替: 要件を「GPU性能・ゲーム性能・マルチ性能でiMac以上」に再定義(単発CPUはiMacに劣ることを仕様書に明記)。
3. 選定の判断はユーザー確認事項: ①9950X3D等へ上げる(消費電力/熱の増加を許容)か、②9800X3D(ゲーム最適)のまま要件を再定義するか。**ユーザー指示「PPTや能力を制限しない」に従い、当面は①の検討(U44)を進める**。
