# 実形状 干渉・埋め込み検査(INTF-01)

- 検査: Blender 評価済みメッシュのBVH交差(`blender/build_imac_pc_v8.py --check-interference`)、562物体、交差対 762。
- 接触のみ(深さ<0.15mm): 338 / 意図した一体・嵌合(ALLOW): 80 / **要対処: 344**

## ALLOW(理由つき)
- グリルのリングとスポークは一体品: 10対
- ファンの羽根とハブは一体品として別メッシュで描いている(実物も一体成形): 60対
- モジュラーソケットは筐体前面の開口に嵌合: 10対

## 要対処(深さ順・上位80)
| 物体A | 物体B | 三角形交差 | AABB重なり[x,y,z] mm | 深さ(近似) |
|---|---|---|---|---|
| stand_neck_shroud | spring_die0 | 122 | [20.0, 20.0, 35.196] | 20.00 |
| stand_neck_shroud | spring_die1 | 122 | [20.0, 20.0, 35.196] | 20.00 |
| cover_filter | ac_inlet_body | 27 | [28.0, 20.0, 26.0] | 20.00 |
| cover_back | ac_inlet_body | 8 | [28.0, 20.0, 26.0] | 20.00 |
| hinge_axle | hinge_friction0 | 96 | [22.0, 12.0, 12.0] | 12.00 |
| hinge_axle | hinge_friction1 | 96 | [22.0, 12.0, 12.0] | 12.00 |
| rad_core | rad_tank_b | 40 | [120.0, 38.0, 12.0] | 12.00 |
| rad_core | rad_tank_a | 32 | [120.0, 38.0, 12.0] | 12.00 |
| pump_cap_lip | pump_housing_body | 35 | [18.5, 9.2, 46.0] | 9.20 |
| gpu_shroud_body | gpu_12v2x6 | 8 | [22.0, 10.0, 9.0] | 9.00 |
| stand_neck_shroud | stand_neck_base | 103 | [124.0, 65.717, 8.0] | 8.00 |
| stand_neck_shroud | cam_guide_rod0_-1 | 48 | [8.0, 8.0, 38.0] | 8.00 |
| stand_neck_shroud | cam_guide_rod0_1 | 48 | [8.0, 8.0, 38.0] | 8.00 |
| stand_neck_shroud | cam_guide_rod1_-1 | 48 | [8.0, 8.0, 38.0] | 8.00 |
| stand_neck_shroud | cam_guide_rod1_1 | 48 | [8.0, 8.0, 38.0] | 8.00 |
| pump_spring0 | pump_screw0 | 324 | [6.4, 7.851, 6.4] | 6.40 |
| pump_spring2 | pump_screw2 | 324 | [6.4, 7.851, 6.4] | 6.40 |
| pump_spring1 | pump_screw1 | 324 | [6.4, 7.851, 6.4] | 6.40 |
| pump_spring3 | pump_screw3 | 324 | [6.4, 7.851, 6.4] | 6.40 |
| vrm_shroud | pump_screw0 | 32 | [6.4, 14.0, 6.4] | 6.40 |
| vrm_shroud | pump_screw1 | 32 | [6.4, 14.0, 6.4] | 6.40 |
| stand_skirt | stand_swivel_stator | 391 | [190.0, 190.0, 6.0] | 6.00 |
| hinge_axle | stand_arm_boss0 | 96 | [6.0, 12.0, 12.0] | 6.00 |
| hinge_axle | stand_arm_boss1 | 96 | [6.0, 12.0, 12.0] | 6.00 |
| stand_neck_shroud | stand_arm0 | 57 | [6.0, 65.278, 38.0] | 6.00 |
| stand_neck_shroud | stand_arm1 | 57 | [6.0, 65.278, 38.0] | 6.00 |
| cam_roller_pin0 | cam_roller0 | 48 | [12.0, 6.0, 6.0] | 6.00 |
| cam_roller_pin1 | cam_roller1 | 48 | [12.0, 6.0, 6.0] | 6.00 |
| stand_neck_shroud | stand_neck_tie | 44 | [112.0, 6.0, 20.0] | 6.00 |
| stand_neck_shroud | stand_neck_cover1 | 36 | [120.0, 6.0, 38.0] | 6.00 |
| hinge_axle | stand_arm_strip0 | 34 | [6.0, 8.0, 6.0] | 6.00 |
| hinge_axle | stand_arm_strip1 | 34 | [6.0, 8.0, 6.0] | 6.00 |
| stand_swivel_stator | stand_swivel_stop_r | 32 | [10.0, 10.0, 6.0] | 6.00 |
| stand_swivel_stator | stand_swivel_stop_l | 32 | [10.0, 10.0, 6.0] | 6.00 |
| stand_arm_strip0 | stand_arm_boss0 | 32 | [6.0, 8.0, 11.0] | 6.00 |
| stand_arm_strip1 | stand_arm_boss1 | 32 | [6.0, 8.0, 11.0] | 6.00 |
| stand_swivel_rotor | stand_swivel_stop_tab | 24 | [10.0, 8.0, 6.0] | 6.00 |
| cover_filter | latch_cam5 | 40 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam2 | 38 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam4 | 38 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam0 | 16 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam1 | 14 | [8.0, 8.0, 5.799] | 5.80 |
| cover_filter | latch_cam3 | 14 | [8.0, 8.0, 5.799] | 5.80 |
| hinge_axle | hinge_tail_lever1 | 60 | [5.0, 12.0, 6.0] | 5.00 |
| hinge_axle | hinge_tail_lever0 | 58 | [5.0, 12.0, 6.0] | 5.00 |
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
| cam_carrier0 | cam_guide_rod0_-1 | 56 | [8.0, 8.0, 4.0] | 4.00 |
| cam_carrier0 | cam_guide_rod0_1 | 56 | [8.0, 8.0, 4.0] | 4.00 |
| cam_carrier1 | cam_guide_rod1_-1 | 56 | [8.0, 8.0, 4.0] | 4.00 |
| cam_carrier1 | cam_guide_rod1_1 | 56 | [8.0, 8.0, 4.0] | 4.00 |
| socket | cap3 | 40 | [6.4, 4.0, 6.4] | 4.00 |
| socket | cap4 | 40 | [6.4, 4.0, 6.4] | 4.00 |
| socket | cap5 | 40 | [6.4, 4.0, 6.4] | 4.00 |
| cover_filter | dowel_pin0 | 33 | [4.0, 8.0, 4.0] | 4.00 |
| cover_filter | dowel_pin1 | 32 | [4.0, 8.0, 4.0] | 4.00 |
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
| vrm_shroud | pump_spring0 | 26 | [7.7, 3.326, 7.7] | 3.33 |
| vrm_shroud | pump_spring1 | 26 | [7.7, 3.326, 7.7] | 3.33 |
| gasket | cover_filter | 338 | [589.599, 3.0, 370.899] | 3.00 |
| hinge_axle | hinge_friction0_cap | 96 | [3.0, 12.0, 12.0] | 3.00 |
| hinge_axle | hinge_friction1_cap | 96 | [3.0, 12.0, 12.0] | 3.00 |
| cover_back | ac_inlet_flange | 46 | [36.0, 28.0, 3.0] | 3.00 |
