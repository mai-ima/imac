# 実形状 干渉・埋め込み検査(INTF-01)

- 検査: Blender 評価済みメッシュのBVH交差(`blender/build_imac_pc_v8.py --check-interference`)、651物体、交差対 738。
- 接触のみ(深さ<0.15mm): 339 / 意図した一体・嵌合(ALLOW): 89 / **要対処: 310**

## ALLOW(理由つき)
- グリルのリングとスポークは一体品: 10対
- 【要モデル化=台帳INTF-03】ヒンジ軸Ø12が各部品のボアを貫通する嵌合。ボア(穴)を未モデルのため重なって検出される: 8対
- ローラはピンに回転嵌合(ボア未モデル=INTF-03): 2対
- ヘッダのプラグは筐体へ1mm嵌合する設計値(基板側のみモデル。ケーブル本体は MDC-FANCABLE で保留): 3対
- ポンプ筐体・キャップ・エルボ・ホース口は一体成形品を複数の基本形で表現(ARCTIC公式の外形): 2対
- ストッパ爪は板にねじ止めされた一体の突起(座面は板内へ埋め込み表現=INTF-03): 3対
- 側板のストリップとボスは一体品を別基本形で表現: 2対
- プラグと受口の嵌合(嵌入量2mmの設計値。実物は受口内へ挿入される): 3対
- ファンの羽根とハブは一体品として別メッシュで描いている(実物も一体成形): 52対
- モジュラーソケットは筐体前面の開口に嵌合: 4対

## 要対処(深さ順・上位80)
| 物体A | 物体B | 三角形交差 | AABB重なり[x,y,z] mm | 深さ(近似) |
|---|---|---|---|---|
| cover_filter | ac_inlet_body | 62 | [28.0, 20.0, 26.0] | 20.00 |
| cover_back | ac_inlet_body | 33 | [28.0, 20.0, 26.0] | 20.00 |
| stand_neck_collar_cap_hole | stand_neck_shroud | 112 | [133.0, 73.217, 8.0] | 8.00 |
| cover_filter | latch_cam0 | 46 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam5 | 46 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam1 | 44 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam2 | 44 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam3 | 44 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam4 | 44 | [8.0, 8.0, 5.799] | 5.80 |
| slab | hinge_bolt0 | 16 | [6.0, 5.0, 6.0] | 5.00 |
| slab | hinge_bolt1 | 16 | [6.0, 5.0, 6.0] | 5.00 |
| slab | hinge_bolt2 | 16 | [6.0, 5.0, 6.0] | 5.00 |
| slab | hinge_bolt3 | 16 | [6.0, 5.0, 6.0] | 5.00 |
| riser0 | riser_gpu_conn | 6 | [5.89, 4.724, 12.0] | 4.72 |
| riser1 | riser_gpu_conn | 6 | [5.89, 4.724, 12.0] | 4.72 |
| riser2 | riser_gpu_conn | 6 | [5.89, 4.724, 12.0] | 4.72 |
| riser3 | riser_gpu_conn | 6 | [5.89, 4.724, 12.0] | 4.72 |
| riser4 | riser_gpu_conn | 6 | [5.89, 4.724, 12.0] | 4.72 |
| riser5 | riser_gpu_conn | 6 | [5.89, 4.724, 12.0] | 4.72 |
| stand_neck_collar_cap_hole | stand_neck_base | 12 | [124.0, 66.278, 4.2] | 4.20 |
| cam_carrier0 | cam_guide_rod0_-1 | 56 | [8.0, 8.0, 4.0] | 4.00 |
| cam_carrier0 | cam_guide_rod0_1 | 56 | [8.0, 8.0, 4.0] | 4.00 |
| cam_carrier1 | cam_guide_rod1_-1 | 56 | [8.0, 8.0, 4.0] | 4.00 |
| cam_carrier1 | cam_guide_rod1_1 | 56 | [8.0, 8.0, 4.0] | 4.00 |
| socket | cap3 | 40 | [6.4, 4.0, 6.4] | 4.00 |
| socket | cap4 | 40 | [6.4, 4.0, 6.4] | 4.00 |
| socket | cap5 | 40 | [6.4, 4.0, 6.4] | 4.00 |
| cover_filter | dowel_pin0 | 37 | [4.0, 8.0, 4.0] | 4.00 |
| cover_filter | dowel_pin1 | 36 | [4.0, 8.0, 4.0] | 4.00 |
| socket | choke3 | 32 | [7.0, 4.0, 7.0] | 4.00 |
| socket | choke4 | 32 | [7.0, 4.0, 7.0] | 4.00 |
| socket | choke5 | 32 | [7.0, 4.0, 7.0] | 4.00 |
| socket | choke6 | 32 | [7.0, 4.0, 7.0] | 4.00 |
| socket | choke7 | 32 | [7.0, 4.0, 7.0] | 4.00 |
| stand_arm0 | stand_neck_cover1 | 27 | [4.0, 6.0, 38.0] | 4.00 |
| stand_neck_cover1 | stand_arm1 | 27 | [4.0, 6.0, 38.0] | 4.00 |
| slab | hinge_doubler | 8 | [144.0, 4.0, 22.0] | 4.00 |
| pump_housing_body | pump_cage_rib1 | 8 | [4.0, 34.8, 4.0] | 4.00 |
| pump_housing_body | pump_cage_rib11 | 8 | [4.0, 34.8, 4.0] | 4.00 |
| cpu_ihs | cap4 | 40 | [6.4, 3.98, 6.4] | 3.98 |
| cpu_ihs | cap5 | 40 | [6.4, 3.98, 6.4] | 3.98 |
| stand_neck_collar_cap_hole | stand_arm0 | 12 | [6.0, 65.278, 3.8] | 3.80 |
| stand_neck_collar_cap_hole | stand_neck_cover1 | 12 | [120.0, 6.0, 3.8] | 3.80 |
| stand_neck_collar_cap_hole | stand_arm1 | 12 | [6.0, 65.278, 3.8] | 3.80 |
| gasket | cover_filter | 355 | [589.599, 3.0, 370.899] | 3.00 |
| hinge_axle | hinge_friction0_cap | 96 | [3.0, 12.0, 12.0] | 3.00 |
| hinge_axle | hinge_friction1_cap | 96 | [3.0, 12.0, 12.0] | 3.00 |
| cover_back | ac_inlet_flange | 53 | [36.0, 28.0, 3.0] | 3.00 |
| cover_filter | ac_inlet_flange | 52 | [36.0, 28.0, 3.0] | 3.00 |
| magnet7 | cover_filter | 33 | [6.799, 3.0, 8.0] | 3.00 |
| cover_filter | magnet5 | 33 | [8.0, 3.0, 6.799] | 3.00 |
| cover_filter | magnet10 | 33 | [6.799, 3.0, 8.0] | 3.00 |
| hinge_backing_plate | hinge_bolt0 | 32 | [6.0, 3.0, 6.0] | 3.00 |
| hinge_backing_plate | hinge_bolt1 | 32 | [6.0, 3.0, 6.0] | 3.00 |
| hinge_backing_plate | hinge_bolt2 | 32 | [6.0, 3.0, 6.0] | 3.00 |
| hinge_backing_plate | hinge_bolt3 | 32 | [6.0, 3.0, 6.0] | 3.00 |
| hinge_bolt_head0 | hinge_bolt0 | 32 | [6.0, 3.0, 6.0] | 3.00 |
| hinge_bolt_head1 | hinge_bolt1 | 32 | [6.0, 3.0, 6.0] | 3.00 |
| hinge_bolt_head2 | hinge_bolt2 | 32 | [6.0, 3.0, 6.0] | 3.00 |
| hinge_bolt_head3 | hinge_bolt3 | 32 | [6.0, 3.0, 6.0] | 3.00 |
| magnet6 | cover_filter | 31 | [6.799, 3.0, 8.0] | 3.00 |
| magnet8 | cover_filter | 31 | [6.799, 3.0, 8.0] | 3.00 |
| cover_filter | magnet0 | 31 | [8.0, 3.0, 6.799] | 3.00 |
| cover_filter | magnet3 | 31 | [8.0, 3.0, 6.799] | 3.00 |
| cover_filter | magnet1 | 31 | [8.0, 3.0, 6.799] | 3.00 |
| cover_filter | magnet4 | 31 | [8.0, 3.0, 6.799] | 3.00 |
| cover_filter | magnet2 | 31 | [8.0, 3.0, 6.799] | 3.00 |
| cover_filter | magnet9 | 31 | [6.799, 3.0, 8.0] | 3.00 |
| cover_filter | magnet11 | 31 | [6.799, 3.0, 8.0] | 3.00 |
| cap2 | socket | 22 | [3.0, 4.0, 6.4] | 3.00 |
| io_shield | board_m2_wifi_module | 16 | [7.9, 3.0, 23.6] | 3.00 |
| ssd_body | m2_screw | 16 | [3.2, 3.0, 3.2] | 3.00 |
| am5_backplate | standoff_board0 | 12 | [5.543, 3.0, 6.4] | 3.00 |
| gasket | dowel_pin0 | 10 | [4.0, 3.0, 4.0] | 3.00 |
| gasket | dowel_pin1 | 10 | [4.0, 3.0, 4.0] | 3.00 |
| slab | hinge_backing_plate | 8 | [140.0, 3.0, 22.0] | 3.00 |
| spring_seat_bot0 | cam_guide_rod0_-1 | 56 | [8.0, 8.0, 2.7] | 2.70 |
| spring_seat_bot0 | cam_guide_rod0_1 | 56 | [8.0, 8.0, 2.7] | 2.70 |
| spring_seat_bot1 | cam_guide_rod1_-1 | 56 | [8.0, 8.0, 2.7] | 2.70 |
| spring_seat_bot1 | cam_guide_rod1_1 | 56 | [8.0, 8.0, 2.7] | 2.70 |
