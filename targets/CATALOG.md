# Right-hand exercise target catalog

Release 0.3-recorded-branch-search. 10 musical targets in the fixed compact-upper native v3 world.

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
  Search: 6/8 accepted starts, 3 distinct candidates; failures {'failed': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.1158457404182911}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).

## nearby-d4

Nearby cross-row contact control; not a movement by itself.

- `realization-51d889f5fcca6222763f`: index r3c5 (D4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Search: 6/8 accepted starts, 6 distinct candidates; failures {'failed': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.0874677334483807}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [independent_sampled_proxy_audit](../experiments/039-search-reliability/warm-coverage/result.json) (SHA256 `da40dc4e953ca1973d21666534a68816d59150002e6eb323ea3300a6150f38ba`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/nearby-d4-candidate-4/overview.png) (SHA256 `498e7e26460efbd3ba0498ae3246363481f63c499e558e76081f29ba91a34194`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/nearby-d4-candidate-4/keyboard.png) (SHA256 `fe6aa43bc4937d5d841513fde5872165c83625e5c50b01ddf06d2633dae06b3b`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/nearby-d4-candidate-4/side.png) (SHA256 `82ba65aa6f5cde90d6dc905d223ffcc2a5414047d416c34b0c014ba31b031c87`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/nearby-d4-candidate-4/hand.png) (SHA256 `6e268a7d2843a8be15248d70ef5b18be4281f04933b16843b8bb02b7e7c1aac0`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/nearby-d4-candidate-4/collision.png) (SHA256 `5b5c44bfa02a72b6b17df88b2e72217bb071489ecf374c184e7faf7ce2b42c30`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).

## upper-g6

Distant upper-register index endpoint, with search branch spread visible.

- `realization-dccc55b028520fafd006`: index r2c15 (G6; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Search: 6/8 accepted starts, 6 distinct candidates; failures {'failed': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.12158587206994569}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [independent_sampled_proxy_audit](../experiments/039-search-reliability/warm-coverage/result.json) (SHA256 `da40dc4e953ca1973d21666534a68816d59150002e6eb323ea3300a6150f38ba`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).

## dyad-c4-csharp4

Semitone dyad with named index/middle contacts; proxy anatomy remains unresolved.

- `realization-7f5cf6375692024ab9f3`: index r1c5 (C4; contact), middle r2c5 (C#4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Search: 6/8 accepted starts, 5 distinct candidates; failures {'failed': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.041243588630146745}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [independent_sampled_proxy_audit](../experiments/039-search-reliability/warm-coverage/result.json) (SHA256 `da40dc4e953ca1973d21666534a68816d59150002e6eb323ea3300a6150f38ba`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).

## dyad-c4-e4

Major-third dyad in a different middle-finger row/column configuration.

- `realization-ecceab87e7b811978197`: index r1c5 (C4; contact), middle r2c6 (E4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'failed': 2, 'invalid_initialization': 1}.
  Search: 6/8 accepted starts, 5 distinct candidates; failures {'failed': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.12723387318900042}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [independent_sampled_proxy_audit](../experiments/039-search-reliability/warm-coverage/result.json) (SHA256 `da40dc4e953ca1973d21666534a68816d59150002e6eb323ea3300a6150f38ba`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/c4-e4-candidate-4/overview.png) (SHA256 `f326d8efd0deb28811064704b222772b695bc483fc45c31ca180ffa2b42e1897`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/c4-e4-candidate-4/keyboard.png) (SHA256 `a1feac31a6cf6f9900eb6e1b97669fb0210d5be9c6e94b3f30c84dacde93977b`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/c4-e4-candidate-4/side.png) (SHA256 `600f81ed5b319a9ec7f65a16bcd5706a138fe463a55710683cd56d7e536f60c5`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/c4-e4-candidate-4/hand.png) (SHA256 `be1dcfc69602e9743d695f98bf044b613bcdd765861c4a6be0e82ad9c5d04f70`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/warm-coverage/renders/c4-e4-candidate-4/collision.png) (SHA256 `e79f451b76d56e14fe3d646c67748aa6ef9c94730af20eabd8fd73a051af8327`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).

## move-c4-d4

Release C4 and establish D4. Found withdrawal/RRT/approach is one sampled strategy.

- `realization-31b36adfe95e86da011c`: index r1c5 (C4; release_after_event) → index r3c5 (D4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2508897879110231}, "index": {"mcp2_abduction_r": 0.04018977801376347, "mcp2_flexion_r": 0.03575833506103776, "md2_flexion_r": 0.22947556646555123, "pm2_flexion_r": 0.1587415176746349}, "middle": {"mcp3_abduction_r": 0.006240945703804929, "mcp3_flexion_r": 0.0017195666428811152, "md3_flexion": 0.022143560585866445, "pm3_flexion_r": 0.00032490235481391627}, "shoulder": {"elv_angle_r": 0.2509595357893687, "shoulder_elv_r": 0.1939611220286953, "shoulder_rot_r": 0.13363914875141303}, "wrist": {"deviation_r": 0.3013722155219152, "flexion_r": 0.24784381832880764}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0176577665141249, "palm_max_excursion_m": 0.02259888730526718, "palm_path_length_m": 0.034683589489978, "sample_count": 187}`.
  Evidence: [path](../experiments/037-upper-anchor-regression/nearby/result.json) (SHA256 `8d40e88a4ecd5bc2fdf3cfa82a36a8d9d8bf083fbde924f3207f19a9ada67623`).
  Evidence: [path](../experiments/039-search-reliability/nearby-alternate/result.json) (SHA256 `cb41d8fca4075be276ec8faa5a262d256b558cfaf57302d34fb24923b4224c84`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/overview.png) (SHA256 `3105ffba015f5979fb31c5a96d16604374a8e74fc7703802d3b50a823741050d`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/keyboard.png) (SHA256 `c27b78d9b39447c2ff506b6d1d424ab96e724833c977f11f29812560a9f58d66`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/side.png) (SHA256 `d0b5e26a3fb23d6de2f64d968922ef1d777704712d569c2d2f9b1885ed1d2fe3`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/hand.png) (SHA256 `ad49b06db1866938274e4140f7e9c8b46d5eac30a95824afda17ac1e5b506714`).
  Evidence: [diagnostic_render](../experiments/038-hand-collision-audit/renders/nearby/collision.png) (SHA256 `855d31940f8168b6e7148771289b7b00dc6956648eb6c9f9bafa648dd0343f5f`).
  Evidence: [independent_sampled_proxy_audit](../experiments/039-search-reliability/nearby-alternate/hand-audit/result.json) (SHA256 `b886e5c2836c415c68321a6b90650522dececf510a7a30deb86743d93c423da3`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/nearby-alternate/hand-audit/renders/nearby-alternate/overview.png) (SHA256 `8bd2b01ae44556f104ac5861f350c8a7cdb2bc4c94a2194b41a1320742eafd5b`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/nearby-alternate/hand-audit/renders/nearby-alternate/keyboard.png) (SHA256 `3e80a29acc887a115e8970f2ecdac89c973d987d37ce905e3388b1bce9a5d990`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/nearby-alternate/hand-audit/renders/nearby-alternate/side.png) (SHA256 `036414a2b427d7371d76b668e5e8570fb19c49b1314c4c38fa44232d811dbc89`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/nearby-alternate/hand-audit/renders/nearby-alternate/hand.png) (SHA256 `fea0fe2deaacbcdba5efc615117f6f80fd8479c43e13a11668b7bb5802717ce2`).
  Evidence: [diagnostic_render](../experiments/039-search-reliability/nearby-alternate/hand-audit/renders/nearby-alternate/collision.png) (SHA256 `eab68278f161bd3b5438f9bdf2ea85692ac64631548425943ca2c6c5f38b6034`).

## move-c4-g6

Long register relocation with a sampled joint path. This is not a necessary minimum movement.

- `realization-3e05258b25f81ceef474`: index r1c5 (C4; release_after_event) → index r2c15 (G6; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.5762076940243945}, "index": {"mcp2_abduction_r": 0.00021724765566558113, "mcp2_flexion_r": 0.3929644463963009, "md2_flexion_r": 0.7491432105210231, "pm2_flexion_r": 0.32731992249447195}, "middle": {"mcp3_abduction_r": 0.008746547336655669, "mcp3_flexion_r": 0.003159430576247735, "md3_flexion": 0.027081932522317928, "pm3_flexion_r": 0.0005225752283695706}, "shoulder": {"elv_angle_r": 0.01683826497691243, "shoulder_elv_r": 0.17449063013500377, "shoulder_rot_r": 0.38903259571198706}, "wrist": {"deviation_r": 0.13315763348056436, "flexion_r": 1.153229905955397}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.015860816702487568, "palm_max_excursion_m": 0.15768396769851392, "palm_path_length_m": 0.16251821055686164, "sample_count": 578}`.
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
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2686595678995972}, "index": {"mcp2_abduction_r": 0.08857839237160152, "mcp2_flexion_r": 0.3814456452023858, "md2_flexion_r": 0.22450543605994455, "pm2_flexion_r": 0.35033904705551344}, "middle": {"mcp3_abduction_r": 0.2010664108026709, "mcp3_flexion_r": 0.4584901357697314, "md3_flexion": 0.0988925511362957, "pm3_flexion_r": 0.4918973999295805}, "shoulder": {"elv_angle_r": 0.05623536577992194, "shoulder_elv_r": 0.17992890931867916, "shoulder_rot_r": 0.10124545260098458}, "wrist": {"deviation_r": 0.2533981290671846, "flexion_r": 0.22118154064907158}}, "maximum_held_envelope_distance_m": 5.423751460937005e-05, "maximum_held_normal_error_rad": 0.0005971087995887229, "maximum_held_position_error_m": 8.147811965408712e-05, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0003022934815981593, "palm_max_excursion_m": 0.05249159122654738, "palm_path_length_m": 0.07128178533842722, "sample_count": 400}`.
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
  Search: 6/8 accepted starts, 3 distinct candidates; failures {'failed': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.1158457404182911}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).
- `realization-a28149e8f939af344c38`: index r4c5 (C4; contact).
  Status: hypothesis; quality: generated_hypothesis; audit: not_evaluated; anatomy unresolved.

Solver history is not a playing trajectory. A found path establishes one sampled model realization; a finite failure is not impossibility. Rigid proxy overlap does not measure tissue penetration. No result establishes a human movement minimum or universal difficulty.
