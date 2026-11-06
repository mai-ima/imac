# ヒンジ/スタンド部品の調査 (2026-11-05, サブエージェント調査。検索ベース・全て原典データシート要確認)

## 保持トルク(調査側の計算, m=19kg, CG: 軸の背面側31mm/高さ190mm)
d(25°)=31cos25+190sin25=108.4mm → T=19×9.81×0.1084≈**20.2N·m**(0°:5.8、-5°:2.7、約-9°で符号反転 → **双方向(対称)の保持が必要**)。当方の概算(docs/joint-analysis.md, m=13.3kg, 軸をドーム中央z=63に置いた場合)は最大±7.5N·m。**差の原因: 質量(19 vs 13.3kg: 実測が必要)と軸位置(CGに対する前後オフセット)**。安全側として設計目標は 20N·m級を想定し、実測質量で確定する。

## 候補(全て単体では不足 → 並列または カウンターバランス併用)
| 候補 | トルク | 寿命 | 必要数(20.2N·m) | 状態 |
|---|---|---|---|---|
| Reell PHT-2.0/4.0/6.0(一方向) | 2/4/6 N·m | 20,000回(目標25,000に不足) | 4個(6N·m品) | https://reell.com/products/friction-hinges/pht |
| Reell PH35(一方向) | 5.65〜11.3 N·m | UNVERIFIED | 2個 | プレスリリースのみ(型番詳細UNVERIFIED) |
| Reell PHC / PHL(対称) | 0〜2.79 / 0.9〜3.4 N·m | 50,000回 | 6〜8個 | 補助摩擦として有望 https://reell.com/product-listings/phl |
| Sugatsune HG-T70S30(2軸) | チルト7N·m(±20%) | UNVERIFIED | 4個(公差考慮) | PDF https://www.sugatsune.com/content/site-assets/501_PDF/HG-T30S15_HG-T70S30.pdf |
| Southco ST-10E-440FJ-33 | 順4.97/逆2.93N·m(非対称) | UNVERIFIED | 5個以上 | monroeengineering掲載 |
| Misumi トルクヒンジ | 最大約5.9N·m | 2万回以上 | 不足 | https://th.misumi-ec.com/en/vona2/detail/221000129063 |
| Ergotron LX HD | UNVERIFIED | | 15kg耐荷重の確認不可 | 本体質量に不適合の可能性 |
Torqmaster/Humanscale/Hanwha/Mitsubishi、ガススプリング、定荷重ばね: UNVERIFIED(要追加調査)。

## Apple iMac(参考)
Apple公式(Late 2012 27")は奥行8in・21lb。チルトのみ(高さ/ピボット無し: HotHardware)。iFixit(EMC 2639)はヒンジが**ばね式**で、ばね保持の**樹脂キャップが劣化すると画面が落下**する(M5金属ワッシャで代替修理)。2012-2014の27インチでヒンジ不具合の事例。 → **教訓: ばね保持部品は金属製にし、寿命試験を行う**。 https://www.ifixit.com/Guide/iMac+Intel+27-Inch+EMC+2639+Hinge+spring+caps+Replacement/134707
