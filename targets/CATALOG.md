# Right-hand exercise target catalog

Release 0.4-first-library. 31 musical targets in the fixed compact-upper native v3 world.

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
| [equivalent-c4](#equivalent-c4) | alternative | C4 | contact_candidates_found | unresolved anatomy |
| [lower-a3](#lower-a3) | baseline | A3 | contact_candidates_found | unresolved anatomy |
| [upper-eflat4](#upper-eflat4) | baseline | Eb4 | contact_candidates_found | unresolved anatomy |
| [same-row-a4](#same-row-a4) | baseline | A4 | contact_candidates_found | unresolved anatomy |
| [cross-b3](#cross-b3) | baseline | B3 | contact_candidates_found | unresolved anatomy |
| [cross-aflat4](#cross-aflat4) | baseline | Ab4 | contact_candidates_found | unresolved anatomy |
| [cross-bflat4](#cross-bflat4) | baseline | Bb4 | contact_candidates_found | unresolved anatomy |
| [equivalent-csharp4](#equivalent-csharp4) | alternative | C#4 | contact_candidates_found, hypothesis | unresolved anatomy |
| [dyad-c4-d4](#dyad-c4-d4) | simultaneous | C4+D4 | contact_candidates_found | unresolved anatomy |
| [dyad-c4-eflat4](#dyad-c4-eflat4) | simultaneous | C4+Eb4 | contact_candidates_found | unresolved anatomy |
| [dyad-c4-f4](#dyad-c4-f4) | simultaneous | C4+F4 | contact_candidates_found | unresolved anatomy |
| [dyad-c4-g4](#dyad-c4-g4) | simultaneous | C4+G4 | contact_candidates_found | unresolved anatomy |
| [move-c4-a3](#move-c4-a3) | relocation | C4 → A3 | sampled_path_found | unresolved anatomy |
| [move-c4-eflat4](#move-c4-eflat4) | relocation | C4 → Eb4 | sampled_path_found | unresolved anatomy |
| [move-c4-a4](#move-c4-a4) | relocation | C4 → A4 | sampled_path_found | unresolved anatomy |
| [move-c4-b3](#move-c4-b3) | relocation | C4 → B3 | sampled_path_found | unresolved anatomy |
| [move-c4-equivalent](#move-c4-equivalent) | relocation | C4 → C4 | sampled_path_found | unresolved anatomy |
| [held-c4-e4-csharp4](#held-c4-e4-csharp4) | held | C4+E4 → C4+C#4 | sampled_path_found | unresolved anatomy |
| [held-c4-csharp4-g4](#held-c4-csharp4-g4) | held | C4+C#4 → C4+G4 | sampled_path_found | unresolved anatomy |
| [return-c4-a3-c4](#return-c4-a3-c4) | sequence | C4 → A3 → C4 | sampled_path_found | unresolved anatomy |
| [alternate-a3-c4-eflat4](#alternate-a3-c4-eflat4) | sequence | A3 → C4 → Eb4 → C4 → A3 | sampled_path_found | unresolved anatomy |
| [return-c4-b3-c4](#return-c4-b3-c4) | sequence | C4 → B3 → C4 | sampled_path_found | unresolved anatomy |

## central-c4

Central index contact control, preserving all discovered pose branches.

- `realization-f0d66b018476cdf7c259`: index r1c5 (C4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 3 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Search: 6/8 accepted starts, 3 distinct candidates; failures {'initial_collision_violation': 2}.
  Unresolved phalangeal proxy distance: -8.716 mm (overlap if negative; not measured tissue).
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
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Search: 6/8 accepted starts, 6 distinct candidates; failures {'initial_collision_violation': 2}.
  Unresolved phalangeal proxy distance: -8.901 mm (overlap if negative; not measured tissue).
  [hand diagnostic](../experiments/039-search-reliability/warm-coverage/renders/nearby-d4-candidate-4/hand.png).
  [collision diagnostic](../experiments/039-search-reliability/warm-coverage/renders/nearby-d4-candidate-4/collision.png).
  Descriptors: `{"candidate_palm_diameter_m": 0.0874677334483807}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [independent_sampled_proxy_audit](../experiments/039-search-reliability/warm-coverage/result.json) (SHA256 `da40dc4e953ca1973d21666534a68816d59150002e6eb323ea3300a6150f38ba`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).

## upper-g6

Distant upper-register index endpoint, with search branch spread visible.

- `realization-dccc55b028520fafd006`: index r2c15 (G6; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Search: 6/8 accepted starts, 6 distinct candidates; failures {'initial_collision_violation': 2}.
  Unresolved phalangeal proxy distance: -10.316 mm (overlap if negative; not measured tissue).
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
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Search: 6/8 accepted starts, 5 distinct candidates; failures {'initial_collision_violation': 2}.
  Unresolved phalangeal proxy distance: -3.115 mm (overlap if negative; not measured tissue).
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
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Search: 6/8 accepted starts, 5 distinct candidates; failures {'initial_collision_violation': 2}.
  Unresolved phalangeal proxy distance: -6.768 mm (overlap if negative; not measured tissue).
  [hand diagnostic](../experiments/039-search-reliability/warm-coverage/renders/c4-e4-candidate-4/hand.png).
  [collision diagnostic](../experiments/039-search-reliability/warm-coverage/renders/c4-e4-candidate-4/collision.png).
  Descriptors: `{"candidate_palm_diameter_m": 0.12723387318900042}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [independent_sampled_proxy_audit](../experiments/039-search-reliability/warm-coverage/result.json) (SHA256 `da40dc4e953ca1973d21666534a68816d59150002e6eb323ea3300a6150f38ba`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).

## move-c4-d4

Release C4 and establish D4. Found withdrawal/RRT/approach is one sampled strategy.

- `realization-31b36adfe95e86da011c`: index r1c5 (C4; release_after_event) → index r3c5 (D4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-5175e9548b8739b550b2`: 261 samples, palm path 63.669 mm.
  Recorded movement `movement-d32404e36dd7cbae2d27`: 187 samples, palm path 34.684 mm.
  Unresolved phalangeal proxy distance: -8.758 mm (overlap if negative; not measured tissue).
  [hand diagnostic](../experiments/038-hand-collision-audit/renders/nearby/hand.png).
  [collision diagnostic](../experiments/038-hand-collision-audit/renders/nearby/collision.png).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2508897879110231}, "index": {"mcp2_abduction_r": 0.04018977801376347, "mcp2_flexion_r": 0.03575833506103776, "md2_flexion_r": 0.22947556646555123, "pm2_flexion_r": 0.1587415176746349}, "middle": {"mcp3_abduction_r": 0.006240945703804929, "mcp3_flexion_r": 0.0017195666428811152, "md3_flexion": 0.022143560585866445, "pm3_flexion_r": 0.00032490235481391627}, "shoulder": {"elv_angle_r": 0.2509595357893687, "shoulder_elv_r": 0.1939611220286953, "shoulder_rot_r": 0.13363914875141303}, "wrist": {"deviation_r": 0.3013722155219152, "flexion_r": 0.24784381832880764}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0176577665141249, "palm_max_excursion_m": 0.02259888730526718, "palm_path_length_m": 0.034683589489978, "sample_count": 187}`.
  Evidence: [path](../experiments/037-upper-anchor-regression/nearby/result.json) (SHA256 `8d40e88a4ecd5bc2fdf3cfa82a36a8d9d8bf083fbde924f3207f19a9ada67623`).
  Evidence: [path](../experiments/039-search-reliability/nearby-alternate/result.json) (SHA256 `cb41d8fca4075be276ec8faa5a262d256b558cfaf57302d34fb24923b4224c84`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [independent_sampled_proxy_audit](../experiments/039-search-reliability/nearby-alternate/hand-audit/result.json) (SHA256 `b886e5c2836c415c68321a6b90650522dececf510a7a30deb86743d93c423da3`).

## move-c4-g6

Long register relocation with a sampled joint path. This is not a necessary minimum movement.

- `realization-3e05258b25f81ceef474`: index r1c5 (C4; release_after_event) → index r2c15 (G6; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Recorded movement `movement-f7ef6e301b14cfe16044`: 578 samples, palm path 162.518 mm.
  Unresolved phalangeal proxy distance: -8.723 mm (overlap if negative; not measured tissue).
  [hand diagnostic](../experiments/038-hand-collision-audit/renders/larger/hand.png).
  [collision diagnostic](../experiments/038-hand-collision-audit/renders/larger/collision.png).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.5762076940243945}, "index": {"mcp2_abduction_r": 0.00021724765566558113, "mcp2_flexion_r": 0.3929644463963009, "md2_flexion_r": 0.7491432105210231, "pm2_flexion_r": 0.32731992249447195}, "middle": {"mcp3_abduction_r": 0.008746547336655669, "mcp3_flexion_r": 0.003159430576247735, "md3_flexion": 0.027081932522317928, "pm3_flexion_r": 0.0005225752283695706}, "shoulder": {"elv_angle_r": 0.01683826497691243, "shoulder_elv_r": 0.17449063013500377, "shoulder_rot_r": 0.38903259571198706}, "wrist": {"deviation_r": 0.13315763348056436, "flexion_r": 1.153229905955397}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.015860816702487568, "palm_max_excursion_m": 0.15768396769851392, "palm_path_length_m": 0.16251821055686164, "sample_count": 578}`.
  Evidence: [path](../experiments/037-upper-anchor-regression/larger/result.json) (SHA256 `9314d7dc50f43f1d1c5209a7c2f96abe9a8e55c021b706a2f1cae318b075d73a`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).

## held-c4-csharp4-e4

Sustain geometric index C4 contact while middle releases C#4 and establishes E4. No holding force or button depression.

- `realization-b7062d1f1a9ec9be2374`: index r1c5 (C4; hold), middle r2c5 (C#4; release_after_event) → index r1c5 (C4; hold), middle r2c6 (E4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-c3da667f1906c13f44f4`: 400 samples, palm path 71.282 mm.
  Unresolved phalangeal proxy distance: -7.418 mm (overlap if negative; not measured tissue).
  [hand diagnostic](../experiments/038-hand-collision-audit/renders/held/hand.png).
  [collision diagnostic](../experiments/038-hand-collision-audit/renders/held/collision.png).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2686595678995972}, "index": {"mcp2_abduction_r": 0.08857839237160152, "mcp2_flexion_r": 0.3814456452023858, "md2_flexion_r": 0.22450543605994455, "pm2_flexion_r": 0.35033904705551344}, "middle": {"mcp3_abduction_r": 0.2010664108026709, "mcp3_flexion_r": 0.4584901357697314, "md3_flexion": 0.0988925511362957, "pm3_flexion_r": 0.4918973999295805}, "shoulder": {"elv_angle_r": 0.05623536577992194, "shoulder_elv_r": 0.17992890931867916, "shoulder_rot_r": 0.10124545260098458}, "wrist": {"deviation_r": 0.2533981290671846, "flexion_r": 0.22118154064907158}}, "maximum_held_envelope_distance_m": 5.423751460937005e-05, "maximum_held_normal_error_rad": 0.0005971087995887229, "maximum_held_position_error_m": 8.147811965408712e-05, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0003022934815981593, "palm_max_excursion_m": 0.05249159122654738, "palm_path_length_m": 0.07128178533842722, "sample_count": 400}`.
  Evidence: [held](../experiments/037-upper-anchor-regression/held/result.json) (SHA256 `5a5bec86896d5e8840487b83137100f826e3765f1a86af28fa11aaea135fb03d`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).

## return-c4-d4-c4

Return-motion hypothesis. Existing outward path alone does not establish the specified return sequence.

- `realization-61c1eb294bc86500b91b`: index r1c5 (C4; release_after_event) → index r3c5 (D4; release_after_event) → index r1c5 (C4; contact).
  Status: hypothesis; quality: generated_hypothesis; audit: not_evaluated; anatomy unresolved.

## equivalent-c4

One musical C4 objective admits r1c5 and r4c5 index realizations in the same exact physical reference. Pose branches remain within each realization.

- `realization-f0d66b018476cdf7c259`: index r1c5 (C4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 3 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Search: 6/8 accepted starts, 3 distinct candidates; failures {'initial_collision_violation': 2}.
  Unresolved phalangeal proxy distance: -8.716 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.1158457404182911}`.
  Evidence: [discovery](../experiments/037-upper-anchor-regression/explore/result.json) (SHA256 `ef1a756d8e6cc69fc036a0b4204e2a8e197a0b9b9d9ea3605ed0d960d94d694d`).
  Evidence: [discovery](../experiments/039-search-reliability/warm-diverse/result.json) (SHA256 `aa5e2a7260d54388951e3246269d78c013bdea690896a645488daab8fb3c7680`).
  Evidence: [independent_endpoint_coverage](../experiments/037-upper-anchor-regression/coverage/result.json) (SHA256 `4ddb687022e883406061f697ba70a2200d134c208640041cf0352339f26754f5`).
  Evidence: [independent_sampled_proxy_audit](../experiments/038-hand-collision-audit/result.json) (SHA256 `b0319eee2564852817775028e4d88876af96227ff50ff8a290a4295068946de3`).
  Evidence: [search_budget_sensitivity](../experiments/039-search-reliability/result.json) (SHA256 `d6a9c91bda9617df2979980724a9a7a6399034928d72754056e1e923860e2950`).
- `realization-a28149e8f939af344c38`: index r4c5 (C4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -8.807 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.06383723032971825}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## lower-a3

A3 endpoint control above C4 on the board; contrasts opposite-direction relocations.

- `realization-594cbc5395f8668649b4`: index r1c4 (A3; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -8.675 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.11465710272228094}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## upper-eflat4

Eb4 endpoint control below C4 on the same row.

- `realization-8723af321a6bd91a1fdd`: index r1c6 (Eb4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -8.754 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.1110069958809491}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## same-row-a4

More distant same-row A4 endpoint; compare directional and joint descriptors, not MIDI distance alone.

- `realization-7c68730e920f1d8b8756`: index r1c8 (A4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -8.719 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.10143729500406154}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## cross-b3

Cross-row B3 endpoint near the C4 region with opposite-direction pitch movement.

- `realization-b887ff4bbf52b5f9670e`: index r3c4 (B3; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -8.950 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.04426809106473178}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## cross-aflat4

Cross-row Ab4 endpoint separates row change from same-row distance controls.

- `realization-daf520d28486fb6b25bf`: index r3c7 (Ab4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -8.889 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.0735987948243278}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## cross-bflat4

Bb4 endpoint at another row/column diagonal; candidate diversity retained.

- `realization-0ed5eb24e6a877c6ee84`: index r2c8 (Bb4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -8.792 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.08471052641683403}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## equivalent-csharp4

Musical C#4 via row5, with row2 as an explicit unsearched single-index alternative. Existing middle C#4 in a dyad is not evidence for that index alternative.

- `realization-3615f567d51e750858eb`: index r5c5 (C#4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 5 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -4.238 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.035039826755460544}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).
- `realization-776c8390357da230401f`: index r2c5 (C#4; contact).
  Status: hypothesis; quality: generated_hypothesis; audit: not_evaluated; anatomy unresolved.

## dyad-c4-d4

Whole-tone dyad across rows, both named contacts required simultaneously.

- `realization-9d6e49ae124540f745fc`: index r1c5 (C4; contact), middle r3c5 (D4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -5.563 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.04470722365193378}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## dyad-c4-eflat4

Same-row minor-third dyad, contrasted with row-changing spans.

- `realization-994616b7bf5e50c37ab8`: index r1c5 (C4; contact), middle r1c6 (Eb4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 5 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -2.992 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.10405246702212027}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## dyad-c4-f4

Fourth dyad with a middle finger on row3; finite branch evidence only.

- `realization-15d2317ba9b80a0a7ca2`: index r1c5 (C4; contact), middle r3c6 (F4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -13.513 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.035973396235094844}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## dyad-c4-g4

Wider fifth dyad; unresolved inactive-digit proxy intersections preclude anatomical feasibility claims.

- `realization-6bda1d4905b511c8b84b`: index r1c5 (C4; contact), middle r2c7 (G4; contact).
  Status: contact_candidates_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Search: 5/8 accepted starts, 4 distinct candidates; failures {'initial_collision_violation': 2, 'Initial pose violates imported joint limits': 1}.
  Unresolved phalangeal proxy distance: -10.761 mm (overlap if negative; not measured tissue).
  Descriptors: `{"candidate_palm_diameter_m": 0.013118323474795964}`.
  Evidence: [discovery](../experiments/040-exercise-library/contact-search/result.json) (SHA256 `c607eb3f53bbfae70aa52b18ff9941ebf44f4b2a386d58c27f653bb68903f842`).
  Evidence: [independent_instrument_endpoint_audit](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/endpoint-hand-audit/result.json) (SHA256 `1500cc7c4628bba2e1794abf955527b894af51540b17ddb86f18742918b69115`).

## move-c4-a3

Same-row move toward lower pitch. Release source, establish destination; no tempo or necessary movement claim.

- `realization-7994c6ed0960237b8e58`: index r1c5 (C4; release_after_event) → index r1c4 (A3; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-37e85b05f05d211b5438`: 237 samples, palm path 56.331 mm.
  Unresolved phalangeal proxy distance: -8.682 mm (overlap if negative; not measured tissue).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2940584989686439}, "index": {"mcp2_abduction_r": 0.08032917543347934, "mcp2_flexion_r": 0.01982855251869453, "md2_flexion_r": 0.05961009661317393, "pm2_flexion_r": 0.128858644437431}, "middle": {"mcp3_abduction_r": 0.004390264980889097, "mcp3_flexion_r": 0.0017195666428811152, "md3_flexion": 0.014818021535165662, "pm3_flexion_r": 0.00017979454935135308}, "shoulder": {"elv_angle_r": 0.3804819665300919, "shoulder_elv_r": 0.17247021421027967, "shoulder_rot_r": 0.06229236430820151}, "wrist": {"deviation_r": 0.1316117585403468, "flexion_r": 0.03804623040287192}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.01201520790656792, "palm_max_excursion_m": 0.043378126145729265, "palm_path_length_m": 0.05633053373741155, "sample_count": 237}`.
  Evidence: [path](../experiments/040-exercise-library/plan-lower/result.json) (SHA256 `f0a1bc42611069743d1f03ba767e38a4143915f46844885262104f6028886559`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).

## move-c4-eflat4

Opposite-direction same-row control; compare palm path and wrist excursion with A3 move.

- `realization-afdce1561569641db10a`: index r1c5 (C4; release_after_event) → index r1c6 (Eb4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-4a788dc514df35bb9d08`: 272 samples, palm path 69.281 mm.
  Unresolved phalangeal proxy distance: -8.764 mm (overlap if negative; not measured tissue).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.46273018905996927}, "index": {"mcp2_abduction_r": 0.0064086910129983465, "mcp2_flexion_r": 0.10138554756245832, "md2_flexion_r": 0.4282306224294942, "pm2_flexion_r": 0.35576215529664185}, "middle": {"mcp3_abduction_r": 0.0082622548342344, "mcp3_flexion_r": 0.002400884851114893, "md3_flexion": 0.02751494808273637, "pm3_flexion_r": 0.00038792397638165443}, "shoulder": {"elv_angle_r": 0.05569833043065775, "shoulder_elv_r": 0.13442505817544714, "shoulder_rot_r": 0.19057689850191156}, "wrist": {"deviation_r": 0.43970514663661886, "flexion_r": 0.07230206627495384}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.015402085458733367, "palm_max_excursion_m": 0.058755475586307726, "palm_path_length_m": 0.06928087269901463, "sample_count": 272}`.
  Evidence: [path](../experiments/040-exercise-library/plan-upper/result.json) (SHA256 `514be1fcbc916be59bb5ff677d1ded20a923441ed6f8b1c8d809816911708f1d`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).

## move-c4-a4

Longer same-row displacement, preserving the exact endpoint branch selected in the recorded search.

- `realization-90b8bf7cc1e66ac6ebd7`: index r1c5 (C4; release_after_event) → index r1c8 (A4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-f37c688201795c85c036`: 308 samples, palm path 91.900 mm.
  Unresolved phalangeal proxy distance: -8.768 mm (overlap if negative; not measured tissue).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.3706418245152706}, "index": {"mcp2_abduction_r": 0.22667192050491486, "mcp2_flexion_r": 0.18955970150437484, "md2_flexion_r": 0.061173209551146746, "pm2_flexion_r": 0.18391343628941814}, "middle": {"mcp3_abduction_r": 0.006484356594269658, "mcp3_flexion_r": 0.002907121132424556, "md3_flexion": 0.028286138149040824, "pm3_flexion_r": 0.0005875763812056567}, "shoulder": {"elv_angle_r": 0.5096746077440463, "shoulder_elv_r": 0.0810953648332341, "shoulder_rot_r": 0.0914000269807182}, "wrist": {"deviation_r": 0.15751890934534468, "flexion_r": 0.038861748875590796}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.009773997508460364, "palm_max_excursion_m": 0.08200710395372758, "palm_path_length_m": 0.09190009009954402, "sample_count": 308}`.
  Evidence: [path](../experiments/040-exercise-library/plan-distant/result.json) (SHA256 `8fda79f7a7fe4bbadd111aed4560ffa53bac761542a8e58498915bdf68a82d71`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).

## move-c4-b3

Cross-row relocation toward lower pitch, with a return sequence using these exact samples.

- `realization-69c43963d6f949378e9f`: index r1c5 (C4; release_after_event) → index r3c4 (B3; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-626d5ac53195999727a9`: 251 samples, palm path 51.747 mm.
  Unresolved phalangeal proxy distance: -9.003 mm (overlap if negative; not measured tissue).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.25435049523331404}, "index": {"mcp2_abduction_r": 0.06363330981511658, "mcp2_flexion_r": 0.04677045600190732, "md2_flexion_r": 0.1889639894613041, "pm2_flexion_r": 0.11702133376562218}, "middle": {"mcp3_abduction_r": 0.00879352209903872, "mcp3_flexion_r": 0.004758363967644952, "md3_flexion": 0.01915753878805708, "pm3_flexion_r": 0.0013660229948394553}, "shoulder": {"elv_angle_r": 0.1980619193419122, "shoulder_elv_r": 0.1074159230418188, "shoulder_rot_r": 0.030063288761253495}, "wrist": {"deviation_r": 0.43171883316035914, "flexion_r": 0.15705117469053376}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0176577665141249, "palm_max_excursion_m": 0.04113629938140089, "palm_path_length_m": 0.051747397076384725, "sample_count": 251}`.
  Evidence: [path](../experiments/040-exercise-library/plan-cross/result.json) (SHA256 `673ef505bea8e8007889ce0017c6b05fede92638d61be5d7e8cb2e73296adc55`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).

## move-c4-equivalent

Repeat musical C4 through a distinct physical row4 button. Geometric relocation and musical interval differ.

- `realization-813dd566562cd5878639`: index r1c5 (C4; release_after_event) → index r4c5 (C4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-e8859667d77d01a2a632`: 251 samples, palm path 52.293 mm.
  Unresolved phalangeal proxy distance: -8.873 mm (overlap if negative; not measured tissue).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2895031551957865}, "index": {"mcp2_abduction_r": 0.05559508571323765, "mcp2_flexion_r": 0.06306531553157102, "md2_flexion_r": 0.24195052532068861, "pm2_flexion_r": 0.20115738926410504}, "middle": {"mcp3_abduction_r": 0.004390264980889097, "mcp3_flexion_r": 0.0032311178828673404, "md3_flexion": 0.02069979422961897, "pm3_flexion_r": 0.0016193874169482259}, "shoulder": {"elv_angle_r": 0.33932606101195645, "shoulder_elv_r": 0.14992643317447074, "shoulder_rot_r": 0.12864851791384146}, "wrist": {"deviation_r": 0.441084571580597, "flexion_r": 0.19850824681089418}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0176577665141249, "palm_max_excursion_m": 0.04139557460836067, "palm_path_length_m": 0.05229314272409587, "sample_count": 251}`.
  Evidence: [path](../experiments/040-exercise-library/plan-equivalent/result.json) (SHA256 `d642ae785733f2d6f4f215265be05f889b267e315bcb16c87530d50e5633a7ba`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).

## held-c4-e4-csharp4

Reverse held-index coordination: sustain index C4 while middle moves E4 to C#4. Direct interpolation rejects; continuation finds a sampled strategy.

- `realization-24aa82c260f65cdd5a59`: index r1c5 (C4; hold), middle r2c6 (E4; release_after_event) → index r1c5 (C4; hold), middle r2c5 (C#4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-01fa7dcdd0857073aad8`: 517 samples, palm path 42.204 mm.
  Unresolved phalangeal proxy distance: -2.744 mm (overlap if negative; not measured tissue).
  [hand diagnostic](../experiments/040-exercise-library/movement-audit/renders/held-reverse/hand.png).
  [collision diagnostic](../experiments/040-exercise-library/movement-audit/renders/held-reverse/collision.png).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.18258691236020497}, "index": {"mcp2_abduction_r": 0.2256053562588864, "mcp2_flexion_r": 0.43856688936043997, "md2_flexion_r": 0.15879222374003543, "pm2_flexion_r": 0.36964350595376017}, "middle": {"mcp3_abduction_r": 0.16948172555492425, "mcp3_flexion_r": 0.5820435718876268, "md3_flexion": 0.3022234336161607, "pm3_flexion_r": 0.8297427788358321}, "shoulder": {"elv_angle_r": 0.03461145214119998, "shoulder_elv_r": 0.07354473135439787, "shoulder_rot_r": 0.05357701866817031}, "wrist": {"deviation_r": 0.06498772186767687, "flexion_r": 0.02820155216676168}}, "maximum_held_envelope_distance_m": 4.4001086748335614e-05, "maximum_held_normal_error_rad": 0.0016683333048237708, "maximum_held_position_error_m": 8.699688195077236e-05, "maximum_registered_penetration_m": 1.6260125454414798e-06, "minimum_joint_margin_rad": 0.0001324086502074162, "palm_max_excursion_m": 0.021139559507532258, "palm_path_length_m": 0.04220367341947312, "sample_count": 517}`.
  Evidence: [held](../experiments/040-exercise-library/held-reverse/result.json) (SHA256 `467b77a66892fbce96b9ac59357d485498888fc25ad376d00ded1b6db11d3a66`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).

## held-c4-csharp4-g4

Wider held-index coordination: sustain C4 while middle changes C#4 to G4. Configured checks pass, but the path has an unresolved 12.636 mm middle/ring proxy overlap. This remains a provisional target hypothesis about real playability.

- `realization-68b5c5327de5563a53f3`: index r1c5 (C4; hold), middle r2c5 (C#4; release_after_event) → index r1c5 (C4; hold), middle r2c7 (G4; contact).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Direct attempt: candidate_rejected; sampled constraints False.
  Recorded movement `movement-c963663158dbc3959a8d`: 622 samples, palm path 88.160 mm.
  Unresolved phalangeal proxy distance: -12.636 mm (overlap if negative; not measured tissue).
  [hand diagnostic](../experiments/040-exercise-library/held-wide-audit/renders/held-wide/hand.png).
  [collision diagnostic](../experiments/040-exercise-library/held-wide-audit/renders/held-wide/collision.png).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.4062634203983193}, "index": {"mcp2_abduction_r": 0.271508419581243, "mcp2_flexion_r": 0.7087696948447325, "md2_flexion_r": 0.601567053000806, "pm2_flexion_r": 0.3738813357023524}, "middle": {"mcp3_abduction_r": 0.20106641080014637, "mcp3_flexion_r": 0.8302589834928983, "md3_flexion": 0.3219783385719116, "pm3_flexion_r": 0.6078254208479635}, "shoulder": {"elv_angle_r": 0.043780122875557215, "shoulder_elv_r": 0.2536257041963498, "shoulder_rot_r": 0.11403888435781781}, "wrist": {"deviation_r": 0.2533981290489262, "flexion_r": 0.305453378048903}}, "maximum_held_envelope_distance_m": 5.423751460937005e-05, "maximum_held_normal_error_rad": 0.0006306643925796837, "maximum_held_position_error_m": 8.147811965408712e-05, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0003022934841226954, "palm_max_excursion_m": 0.06944465255151532, "palm_path_length_m": 0.08815962760566984, "sample_count": 622}`.
  Evidence: [held](../experiments/040-exercise-library/held-wide/result.json) (SHA256 `a36cde96836f6bb8e6f8f3d74b86763434abc59a7105c18d6bb8077baaddc6ef`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/held-wide-audit/result.json) (SHA256 `ab57106a26b0bed000db4da4e27ed9a1040c59d9bc9c52b8811d4db3c8e82a9d`).

## return-c4-a3-c4

Three-event same-row return composed from a found path and its exact reversed sampled kinematics; no timing or dynamics.

- `realization-cba23cc24e5f662df794`: index r1c5 (C4; release_after_event) → index r1c4 (A3; release_after_event) → index r1c5 (C4; release_after_event).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Recorded movement `movement-0ec2aff6d42bee1c5f43`: 473 samples, palm path 112.661 mm.
  Unresolved phalangeal proxy distance: -8.682 mm (overlap if negative; not measured tissue).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2940584989686439}, "index": {"mcp2_abduction_r": 0.08032917543347934, "mcp2_flexion_r": 0.01982855251869453, "md2_flexion_r": 0.05961009661317393, "pm2_flexion_r": 0.128858644437431}, "middle": {"mcp3_abduction_r": 0.004390264980889097, "mcp3_flexion_r": 0.0017195666428811152, "md3_flexion": 0.014818021535165662, "pm3_flexion_r": 0.00017979454935135308}, "shoulder": {"elv_angle_r": 0.3804819665300919, "shoulder_elv_r": 0.17247021421027967, "shoulder_rot_r": 0.06229236430820151}, "wrist": {"deviation_r": 0.1316117585403468, "flexion_r": 0.03804623040287192}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.01201520790656792, "palm_max_excursion_m": null, "palm_path_length_m": 0.1126610674748231, "sample_count": 473}`.
  Evidence: [sequence](../experiments/040-exercise-library/sequences/result.json) (SHA256 `4a6f1316fd5f2208c110399c4dfda1592044734d3c6839513175766adf94bce1`).
  Evidence: [sequence_segment](../experiments/040-exercise-library/sequences/../plan-lower/result.json) (SHA256 `f0a1bc42611069743d1f03ba767e38a4143915f46844885262104f6028886559`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).

## alternate-a3-c4-eflat4

Five-event direction alternation through a shared exact C4 pose. Each segment has independent sampled proxy audits; all joins preserve qpos exactly.

- `realization-f8f2afc77957a349c9c9`: index r1c4 (A3; release_after_event) → index r1c5 (C4; release_after_event) → index r1c6 (Eb4; release_after_event) → index r1c5 (C4; release_after_event) → index r1c4 (A3; release_after_event).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Recorded movement `movement-4fe6584f55c57a340eea`: 1015 samples, palm path 251.223 mm.
  Unresolved phalangeal proxy distance: -8.764 mm (overlap if negative; not measured tissue).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.7401248030267158}, "index": {"mcp2_abduction_r": 0.08258485648887087, "mcp2_flexion_r": 0.10138554756245832, "md2_flexion_r": 0.4554951414581455, "pm2_flexion_r": 0.47038770611954267}, "middle": {"mcp3_abduction_r": 0.0082622548342344, "mcp3_flexion_r": 0.002400884851114893, "md3_flexion": 0.02751494808273637, "pm3_flexion_r": 0.00038792397638165443}, "shoulder": {"elv_angle_r": 0.3804819665300919, "shoulder_elv_r": 0.29306550524643404, "shoulder_rot_r": 0.24301175903810518}, "wrist": {"deviation_r": 0.5530424485062125, "flexion_r": 0.07251340222618496}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.01201520790656792, "palm_max_excursion_m": null, "palm_path_length_m": 0.25122281287285236, "sample_count": 1015}`.
  Evidence: [sequence](../experiments/040-exercise-library/sequences/result.json) (SHA256 `4a6f1316fd5f2208c110399c4dfda1592044734d3c6839513175766adf94bce1`).
  Evidence: [sequence_segment](../experiments/040-exercise-library/sequences/../plan-lower/result.json) (SHA256 `f0a1bc42611069743d1f03ba767e38a4143915f46844885262104f6028886559`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).
  Evidence: [sequence_segment](../experiments/040-exercise-library/sequences/../plan-upper/result.json) (SHA256 `514be1fcbc916be59bb5ff677d1ded20a923441ed6f8b1c8d809816911708f1d`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).

## return-c4-b3-c4

Three-event cross-row return; sequence provenance preserves forward/reverse traversal of the same actually audited path samples.

- `realization-e62be601d55fbc49a902`: index r1c5 (C4; release_after_event) → index r3c4 (B3; release_after_event) → index r1c5 (C4; release_after_event).
  Status: sampled_path_found; quality: independently_audited; audit: all_saved_candidates_audited_anatomy_unresolved; anatomy unresolved.
  Recorded movement `movement-f6fd12ed316411e2ae76`: 501 samples, palm path 103.495 mm.
  Unresolved phalangeal proxy distance: -9.003 mm (overlap if negative; not measured tissue).
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.25435049523331404}, "index": {"mcp2_abduction_r": 0.06363330981511658, "mcp2_flexion_r": 0.04677045600190732, "md2_flexion_r": 0.1889639894613041, "pm2_flexion_r": 0.11702133376562218}, "middle": {"mcp3_abduction_r": 0.00879352209903872, "mcp3_flexion_r": 0.004758363967644952, "md3_flexion": 0.01915753878805708, "pm3_flexion_r": 0.0013660229948394553}, "shoulder": {"elv_angle_r": 0.1980619193419122, "shoulder_elv_r": 0.1074159230418188, "shoulder_rot_r": 0.030063288761253495}, "wrist": {"deviation_r": 0.43171883316035914, "flexion_r": 0.15705117469053376}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": 0.0, "minimum_joint_margin_rad": 0.0176577665141249, "palm_max_excursion_m": null, "palm_path_length_m": 0.10349479415276945, "sample_count": 501}`.
  Evidence: [sequence](../experiments/040-exercise-library/sequences/result.json) (SHA256 `4a6f1316fd5f2208c110399c4dfda1592044734d3c6839513175766adf94bce1`).
  Evidence: [sequence_segment](../experiments/040-exercise-library/sequences/../plan-cross/result.json) (SHA256 `673ef505bea8e8007889ce0017c6b05fede92638d61be5d7e8cb2e73296adc55`).
  Evidence: [independent_sampled_proxy_audit](../experiments/040-exercise-library/movement-audit/result.json) (SHA256 `628a36438e0858cc4aff327cb21cd8acb4d2c1418e979bceca15cb2114e9183c`).
  Evidence: [independent_endpoint_coverage](../experiments/040-exercise-library/endpoint-coverage/result.json) (SHA256 `e5d07397c88d46c9d774789549033ee8290a3c65efc939af920a1dafb93c793d`).

Solver history is not a playing trajectory. A found path establishes one sampled model realization; a finite failure is not impossibility. Rigid proxy overlap does not measure tissue penetration. No result establishes a human movement minimum or universal difficulty.
