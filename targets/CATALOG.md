# Right-hand exercise target catalog

Release 0.2-proxy-audited. 10 musical targets in the fixed compact-upper native v3 world.

**Provisional model challenges. Human feasibility is unknown for every entry.**

Index/middle contacts only. Torso, legs, left arm, treble/bass cases and closed bellows remain fixed. No tempo, force or button depression is inferred.

Use `uv run aec targets list --family held`, `uv run aec targets show TARGET_ID`, and `uv run aec targets verify TARGET_ID`. Verification checks commitments, not scientific validity.

| Target | Family | Notes | Search status | Audit |
|---|---|---|---|---|
| [central-c4](#central-c4) | baseline | C4 | contact_candidates_found | unresolved anatomy |
| [nearby-d4](#nearby-d4) | baseline | D4 | contact_candidates_found | unresolved anatomy |
| [upper-g6](#upper-g6) | baseline | G6 | contact_candidates_found | unresolved anatomy |
| [dyad-c4-csharp4](#dyad-c4-csharp4) | simultaneous | C4+C#4 | contact_candidates_found | unresolved anatomy |
| [dyad-c4-e4](#dyad-c4-e4) | simultaneous | C4+E4 | contact_candidates_found | unresolved anatomy |
| [move-c4-d4](#move-c4-d4) | relocation | C4 → D4 | sampled_path_found | unresolved anatomy |
| [move-c4-g6](#move-c4-g6) | relocation | C4 → G6 | sampled_path_found | unresolved anatomy |
| [held-c4-csharp4-e4](#held-c4-csharp4-e4) | held | C4+C#4 → C4+E4 | sampled_path_found | unresolved anatomy |
| [return-c4-d4-c4](#return-c4-d4-c4) | sequence | C4 → D4 → C4 | hypothesis | unresolved anatomy |
| [equivalent-c4](#equivalent-c4) | alternative | C4 | contact_candidates_found, hypothesis | unresolved anatomy |

## central-c4

Central index contact control, preserving all discovered pose branches.

- `realization-f0d66b018476cdf7c259`: index r1c5 (C4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 3 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Descriptors: `{"candidate_palm_diameter_m": 0.1158457404182911}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).

## nearby-d4

Nearby cross-row contact control; not a movement by itself.

- `realization-51d889f5fcca6222763f`: index r3c5 (D4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Descriptors: `{"candidate_palm_diameter_m": 0.0874677334483807}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).

## upper-g6

Distant upper-register index endpoint, with search branch spread visible.

- `realization-dccc55b028520fafd006`: index r2c15 (G6; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Descriptors: `{"candidate_palm_diameter_m": 0.09167141841146714}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).

## dyad-c4-csharp4

Semitone dyad with named index/middle contacts; proxy anatomy remains unresolved.

- `realization-7f5cf6375692024ab9f3`: index r1c5 (C4; contact), middle r2c5 (C#4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Descriptors: `{"candidate_palm_diameter_m": 0.030059176401632037}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).

## dyad-c4-e4

Major-third dyad in a different middle-finger row/column configuration.

- `realization-ecceab87e7b811978197`: index r1c5 (C4; contact), middle r2c6 (E4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Descriptors: `{"candidate_palm_diameter_m": 0.10499134969328215}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).

## move-c4-d4

Release C4 and establish D4. Found withdrawal/RRT/approach is one sampled strategy.

- `realization-31b36adfe95e86da011c`: index r1c5 (C4; release_after_event) → index r3c5 (D4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.30952379525317597}, "index": {"mcp2_abduction_r": 0.008673302570774144, "mcp2_flexion_r": 0.011054171875030994, "md2_flexion_r": 0.33691979806286554, "pm2_flexion_r": 0.3597863659263338}, "middle": {"mcp3_abduction_r": 0.005337882485280804, "mcp3_flexion_r": 0.0021742008436966276, "md3_flexion": 0.020683722600833912, "pm3_flexion_r": 0.00031353842816461697}, "shoulder": {"elv_angle_r": 0.43302143017745354, "shoulder_elv_r": 0.3552552076517862, "shoulder_rot_r": 0.19769206263636932}, "wrist": {"deviation_r": 0.4446306927653995, "flexion_r": 0.28022946398322285}}, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.015877412427995702, "palm_max_excursion_m": 0.049497760650161246, "palm_path_length_m": 0.06366852477103843, "sample_count": 261}`.
  Evidence: [path](../experiments/037-upper-anchor-regression/nearby/result.json) (SHA256 `8d40e88a4ecd5bc2fdf3cfa82a36a8d9d8bf083fbde924f3207f19a9ada67623`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/overview.png) (SHA256 `3105ffba015f5979fb31c5a96d16604374a8e74fc7703802d3b50a823741050d`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/keyboard.png) (SHA256 `c27b78d9b39447c2ff506b6d1d424ab96e724833c977f11f29812560a9f58d66`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/side.png) (SHA256 `d0b5e26a3fb23d6de2f64d968922ef1d777704712d569c2d2f9b1885ed1d2fe3`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/hand.png) (SHA256 `ad49b06db1866938274e4140f7e9c8b46d5eac30a95824afda17ac1e5b506714`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/collision.png) (SHA256 `855d31940f8168b6e7148771289b7b00dc6956648eb6c9f9bafa648dd0343f5f`).

## move-c4-g6

Long register relocation with a sampled joint path. This is not a necessary minimum movement.

- `realization-3e05258b25f81ceef474`: index r1c5 (C4; release_after_event) → index r2c15 (G6; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.5762076940243945}, "index": {"mcp2_abduction_r": 0.00021724765566558113, "mcp2_flexion_r": 0.3929644463963009, "md2_flexion_r": 0.7491432105210231, "pm2_flexion_r": 0.32731992249447195}, "middle": {"mcp3_abduction_r": 0.008746547336655669, "mcp3_flexion_r": 0.003159430576247735, "md3_flexion": 0.027081932522317928, "pm3_flexion_r": 0.0005225752283695706}, "shoulder": {"elv_angle_r": 0.01683826497691243, "shoulder_elv_r": 0.17449063013500377, "shoulder_rot_r": 0.38903259571198706}, "wrist": {"deviation_r": 0.13315763348056436, "flexion_r": 1.153229905955397}}, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.015860816702487568, "palm_max_excursion_m": 0.15768396769851392, "palm_path_length_m": 0.16251821055686164, "sample_count": 578}`.
  Evidence: [path](../experiments/037-upper-anchor-regression/larger/result.json) (SHA256 `9314d7dc50f43f1d1c5209a7c2f96abe9a8e55c021b706a2f1cae318b075d73a`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/larger/overview.png) (SHA256 `b6a6f8680585627060f6f14c5bae9202596f00862bf4b7e6a2eea0cc6babe509`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/larger/keyboard.png) (SHA256 `82e1e283390cf2bf89a33cf10c33434d093e02e7cf79f786a052f870c3218844`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/larger/side.png) (SHA256 `f63e578c9b35e1d1d13dccced543cb07a845cf6e83ad1bb24140a1d1b0440ae5`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/larger/hand.png) (SHA256 `8afc2aae0b640122b87d749750eb9c54a25cf76b0eb6916b3de292e96b79dc70`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/larger/collision.png) (SHA256 `165a6615772137f3ea6cdfc1ac669d41f729f343ae5d9b18a50fe59be43887aa`).

## held-c4-csharp4-e4

Sustain geometric index C4 contact while middle releases C#4 and establishes E4. No holding force or button depression.

- `realization-b7062d1f1a9ec9be2374`: index r1c5 (C4; hold), middle r2c5 (C#4; release_after_event) → index r1c5 (C4; hold), middle r2c6 (E4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2686595678995972}, "index": {"mcp2_abduction_r": 0.08857839237160152, "mcp2_flexion_r": 0.3814456452023858, "md2_flexion_r": 0.22450543605994455, "pm2_flexion_r": 0.35033904705551344}, "middle": {"mcp3_abduction_r": 0.2010664108026709, "mcp3_flexion_r": 0.4584901357697314, "md3_flexion": 0.0988925511362957, "pm3_flexion_r": 0.4918973999295805}, "shoulder": {"elv_angle_r": 0.05623536577992194, "shoulder_elv_r": 0.17992890931867916, "shoulder_rot_r": 0.10124545260098458}, "wrist": {"deviation_r": 0.2533981290671846, "flexion_r": 0.22118154064907158}}, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0003022934815981593, "palm_max_excursion_m": 0.05249159122654738, "palm_path_length_m": 0.07128178533842722, "sample_count": 400}`.
  Evidence: [held](../experiments/037-upper-anchor-regression/held/result.json) (SHA256 `5a5bec86896d5e8840487b83137100f826e3765f1a86af28fa11aaea135fb03d`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/held/overview.png) (SHA256 `4aacc527dd0380faa81cd86e5d2fe546cd5775b5246a072d07abbf2996b9f0bb`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/held/keyboard.png) (SHA256 `1f5ae107741e725c88adb50d41e67d9d97b99ac54c92ff0c25ee1930a78702fe`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/held/side.png) (SHA256 `a9a7cab2b08e91cb2ef9ef54748e352ff71b53595c4e61bbe846e59da8332346`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/held/hand.png) (SHA256 `fc96c4fed46103db1ef7b9c4f1122e11045d5ea424838f7058298ac55da42d95`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/held/collision.png) (SHA256 `9be6c017760efd1480fef48b246338a063fe1835389e78ae4030ef9a23a82a4f`).

## return-c4-d4-c4

Return-motion hypothesis. Existing outward path alone does not establish the specified return sequence.

- `realization-61c1eb294bc86500b91b`: index r1c5 (C4; release_after_event) → index r3c5 (D4; release_after_event) → index r1c5 (C4; contact).
  Status: hypothesis; quality: generated_hypothesis; audit: not_evaluated; anatomy unresolved.

## equivalent-c4

One musical C4 target with distinct physical buttons. Second realization remains a hypothesis until exact-world search.

- `realization-f0d66b018476cdf7c259`: index r1c5 (C4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 3 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Descriptors: `{"candidate_palm_diameter_m": 0.1158457404182911}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
- `realization-a28149e8f939af344c38`: index r4c5 (C4; contact).
  Status: hypothesis; quality: generated_hypothesis; audit: not_evaluated; anatomy unresolved.

Solver history is not a playing trajectory. A found path establishes one sampled model realization; a finite failure is not impossibility. Rigid proxy overlap does not measure tissue penetration. No result establishes a human movement minimum or universal difficulty.
