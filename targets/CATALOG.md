# Right-hand exercise target catalog

Release 0.7-autonomous-generated-challenges. 50 musical targets in the fixed compact-upper native v3 world.

**Provisional model challenges. Human feasibility is unknown for every entry.**

Named five-finger contacts. Torso, legs, left arm, treble/bass cases and closed bellows remain fixed. No tempo, force or button depression is inferred.

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
| [five-finger-thumb](#five-finger-thumb) | five-finger-control | C4 | contact_candidates_found | unresolved anatomy |
| [five-finger-index](#five-finger-index) | five-finger-control | C4 | contact_candidates_found | unresolved anatomy |
| [five-finger-middle](#five-finger-middle) | five-finger-control | C4 | contact_candidates_found | unresolved anatomy |
| [five-finger-ring](#five-finger-ring) | five-finger-control | C4 | contact_candidates_found | unresolved anatomy |
| [five-finger-little](#five-finger-little) | five-finger-control | C4 | contact_candidates_found | unresolved anatomy |
| [five-finger-index-ring](#five-finger-index-ring) | five-finger-control | C4+E4 | contact_candidates_found | unresolved anatomy |
| [five-finger-index-little](#five-finger-index-little) | five-finger-control | C4+E4 | not_found_with_current_search | unresolved anatomy |
| [five-finger-three-long](#five-finger-three-long) | five-finger-control | C4+C#4+D4 | not_found_with_current_search | unresolved anatomy |
| [five-finger-thumb-index](#five-finger-thumb-index) | five-finger-control | C4+C#4 | not_found_with_current_search | unresolved anatomy |
| [passage-stepwise](#passage-stepwise) | sequence | C4 → D4 → E4 | sampled_path_found | unresolved anatomy |
| [passage-repetition](#passage-repetition) | repetition | C4 → C4 → C4 | sampled_path_found | unresolved anatomy |
| [passage-thumb-reversal](#passage-thumb-reversal) | reversal | C4 → Eb4 → C4 | sampled_path_found | unresolved anatomy |
| [passage-held-ring](#passage-held-ring) | held | C4+E4 → C4+F4 | no_complete_passage_found | unresolved anatomy |
| [passage-held-repeat](#passage-held-repeat) | held | C4+E4 → C4+E4 | no_complete_passage_found | unresolved anatomy |
| [generated-07ec8d2638eb010f](#generated-07ec8d2638eb010f) | stepwise | D4 → C4 → D4 → E4 | sampled_path_found | unresolved anatomy |
| [generated-945a2c839056ef55](#generated-945a2c839056ef55) | repetition | D4 → D4 → Eb4 | sampled_path_found | unresolved anatomy |
| [generated-71ba0dd640884d91](#generated-71ba0dd640884d91) | reversal | D4 → E4 → C#4 | sampled_path_found | unresolved anatomy |
| [generated-dcbc77238f1b5559](#generated-dcbc77238f1b5559) | arpeggio | Eb4 → G4 → Bb4 → Eb4 | sampled_path_found | unresolved anatomy |
| [generated-247e3482c25d6082](#generated-247e3482c25d6082) | held | D4 → D4+G4 → D4+E4 → D4+E4 | no_complete_passage_found | unresolved anatomy |

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

## five-finger-thumb

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-e777c6a9e13c8a112998`: thumb r1c5 (C4; contact).
  Status: contact_candidates_found; quality: numerically_realized; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 3/5 accepted starts, 3 distinct candidates; failures {'initial_collision_violation': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.021285176266812922}`.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [matched_policy_comparison](../experiments/041-five-finger-contacts/comparison/result.json) (SHA256 `0874cc33af8388e7d51edf1e5fbb3246568dbd3262977d7ac68e34c2f924597f`).
  Evidence: [matched_policy_comparison](../experiments/041-five-finger-contacts/comparison/thumb-policy-hand.png) (SHA256 `4043851685da0adbf637f03db3701307ce9d1d2e5155eda6a7160cd16ce6b9a5`).
  Evidence: [matched_policy_comparison](../experiments/041-five-finger-contacts/comparison/thumb-policy-contact_collision.png) (SHA256 `af8c1ca56586495ac25d2e79b791bfb36d30928eb793a782bf183ded23a420bd`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## five-finger-index

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-f0d66b018476cdf7c259`: index r1c5 (C4; contact).
  Status: contact_candidates_found; quality: numerically_realized; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 3/5 accepted starts, 2 distinct candidates; failures {'initial_collision_violation': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.06956871177734379}`.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## five-finger-middle

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-1ad83ed5bd0685a13b0e`: middle r1c5 (C4; contact).
  Status: contact_candidates_found; quality: numerically_realized; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 3/5 accepted starts, 3 distinct candidates; failures {'initial_collision_violation': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.06283181185577469}`.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## five-finger-ring

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-ecb05c2e778787271c01`: ring r1c5 (C4; contact).
  Status: contact_candidates_found; quality: numerically_realized; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 3/5 accepted starts, 3 distinct candidates; failures {'initial_collision_violation': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.07733067819908876}`.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [supplemental_contact_detail](../experiments/041-five-finger-contacts/ring-detail/result.json) (SHA256 `7233fa95957690b64e6b7610b0b4d0ef477465c66611197af605359711bd49d9`).
  Evidence: [supplemental_contact_detail](../experiments/041-five-finger-contacts/ring-detail/renders/ring-candidate-0/contact.png) (SHA256 `e73f2d03f1b0cc05250ce6099045c5bb1b9d7f0c3b6c5cd1b7756e95b29752b2`).
  Evidence: [supplemental_contact_detail](../experiments/041-five-finger-contacts/ring-detail/renders/ring-candidate-0/contact_collision.png) (SHA256 `35d5e3bca284bb09695b6f137a693beaf29c16dd4e079367c5a5f1c981920c04`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## five-finger-little

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-71d56d8a44b39417bde2`: little r1c5 (C4; contact).
  Status: contact_candidates_found; quality: numerically_realized; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 3/5 accepted starts, 3 distinct candidates; failures {'initial_collision_violation': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.04942791840823652}`.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## five-finger-index-ring

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-c8cdd6ce9056386841cb`: index r1c5 (C4; contact), ring r2c6 (E4; contact).
  Status: contact_candidates_found; quality: numerically_realized; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 3/5 accepted starts, 2 distinct candidates; failures {'initial_collision_violation': 2}.
  Descriptors: `{"candidate_palm_diameter_m": 0.0008252000800606455}`.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## five-finger-index-little

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-a01a17264888fa55453b`: index r1c5 (C4; contact), little r2c6 (E4; contact).
  Status: not_found_with_current_search; quality: generated_hypothesis; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 0/5 accepted starts, 0 distinct candidates; failures {'iteration_budget_exhausted': 3, 'initial_collision_violation': 2}.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## five-finger-three-long

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-575edba33db8b9c45026`: index r1c5 (C4; contact), middle r2c5 (C#4; contact), ring r3c5 (D4; contact).
  Status: not_found_with_current_search; quality: generated_hypothesis; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 0/5 accepted starts, 0 distinct candidates; failures {'iteration_budget_exhausted': 3, 'initial_collision_violation': 2}.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## five-finger-thumb-index

Named digit contact control with unassigned digits permitted to articulate; finite local search and unresolved anatomy.

- `realization-4891bcf6c36d6245770d`: thumb r1c5 (C4; contact), index r2c5 (C#4; contact).
  Status: not_found_with_current_search; quality: generated_hypothesis; audit: endpoints_only_anatomy_unresolved; anatomy unresolved.
  Search: 0/5 accepted starts, 0 distinct candidates; failures {'no_sampled_clear_step': 2, 'iteration_budget_exhausted': 1, 'initial_collision_violation': 2}.
  Evidence: [discovery](../experiments/041-five-finger-contacts/free/result.json) (SHA256 `0398c02d76ef46e3b4e8b0592155891ff864a51f24c8963d1e0bcd83e2a4166e`).
  Evidence: [independent_endpoint_coverage](../experiments/041-five-finger-contacts/coverage/result.json) (SHA256 `2768824e902840110e44b5eb6d8f2ca90cb0fd440d7a7a64ecc508c3f3f5fc2f`).
  Evidence: [independent_contact_report](../experiments/041-five-finger-contacts/diagnostics/result.json) (SHA256 `3a237aece006c1e94b81546918a6d47bb05d05672ed241d410f46991ceccd7eb`).

## passage-stepwise

C4–D4–E4 bounded whole-hand beam search; alternate E4 button/finger strategies, with preparation failures preserved.

[connected_passage_search](../experiments/042-connected-fingerings/stepwise/result.json).
[passage_media_audit](../experiments/042-connected-fingerings/stepwise-media/result.json).
[search_diagram](../experiments/042-connected-fingerings/stepwise-media/search.svg).
[animation](../experiments/042-connected-fingerings/stepwise-media/strategy-0/trajectory.gif).
[animation](../experiments/042-connected-fingerings/stepwise-media/strategy-1/trajectory.gif).
- `realization-3b107e386c31f199e507`: middle r4c5 (C4; release_after_event) → little r3c5 (D4; release_after_event) → index r5c6 (E4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-0`: 522 samples, palm path 75.193 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.4713435438802869}, "index": {"mcp2_abduction_r": 0.4216475194776008, "mcp2_flexion_r": 0.06780384214668611, "md2_flexion_r": 0.8081334720335681, "pm2_flexion_r": 0.5036834045728422}, "middle": {"mcp3_abduction_r": 0.09983365340566458, "mcp3_flexion_r": 0.1408936802695394, "md3_flexion": 0.04304374179792683, "pm3_flexion_r": 0.0889861939487826}, "shoulder": {"elv_angle_r": 0.5614694876550368, "shoulder_elv_r": 0.16738871556053492, "shoulder_rot_r": 0.13598614061457825}, "wrist": {"deviation_r": 0.5601965767937422, "flexion_r": 0.6813612292392246}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.07519257163752344, "sample_count": 522}`.
  Evidence: [connected_passage_search](../experiments/042-connected-fingerings/stepwise/result.json) (SHA256 `9f1a5008107bb6496846adb71aa0aa4defefc312f99c2aa045bf7a9b2fcb57f5`).
  Evidence: [passage_media_audit](../experiments/042-connected-fingerings/stepwise-media/result.json) (SHA256 `5dc1b9addd834a2390430ec425dcbcfb577664a4c318b495712ba858c0e74385`).
  Evidence: [search_diagram](../experiments/042-connected-fingerings/stepwise-media/search.svg) (SHA256 `e11b57ab3243ad177a90ed811cdbc97038f8530366da4fb3bcb5c07cc599fd4e`).
  Evidence: [animation](../experiments/042-connected-fingerings/stepwise-media/strategy-0/trajectory.gif) (SHA256 `326e2ecbe97359d291c233e2ceea9ec1510a46be9c978be30a02e43bb125a68b`).
  Evidence: [animation](../experiments/042-connected-fingerings/stepwise-media/strategy-1/trajectory.gif) (SHA256 `4d054f1dbe5fed788441a59874fe236613150e66e8241aca31eac586408f8629`).
- `realization-21f61c0421c88004e8f9`: middle r4c5 (C4; release_after_event) → little r3c5 (D4; release_after_event) → ring r2c6 (E4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-1`: 656 samples, palm path 84.208 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.5305147037033671}, "index": {"mcp2_abduction_r": 0.1213588593855402, "mcp2_flexion_r": 0.3232202550829084, "md2_flexion_r": 0.8080211290353224, "pm2_flexion_r": 0.0785744760033702}, "middle": {"mcp3_abduction_r": 0.05890504948793718, "mcp3_flexion_r": 0.1769273652169493, "md3_flexion": 0.043483916999209477, "pm3_flexion_r": 0.09784674442540298}, "shoulder": {"elv_angle_r": 0.738812065990079, "shoulder_elv_r": 0.07858810744229433, "shoulder_rot_r": 0.054557638452118334}, "wrist": {"deviation_r": 0.21715231323261464, "flexion_r": 0.8874189946293404}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.08420789604634542, "sample_count": 656}`.
  Evidence: [connected_passage_search](../experiments/042-connected-fingerings/stepwise/result.json) (SHA256 `9f1a5008107bb6496846adb71aa0aa4defefc312f99c2aa045bf7a9b2fcb57f5`).
  Evidence: [passage_media_audit](../experiments/042-connected-fingerings/stepwise-media/result.json) (SHA256 `5dc1b9addd834a2390430ec425dcbcfb577664a4c318b495712ba858c0e74385`).
  Evidence: [search_diagram](../experiments/042-connected-fingerings/stepwise-media/search.svg) (SHA256 `e11b57ab3243ad177a90ed811cdbc97038f8530366da4fb3bcb5c07cc599fd4e`).
  Evidence: [animation](../experiments/042-connected-fingerings/stepwise-media/strategy-0/trajectory.gif) (SHA256 `326e2ecbe97359d291c233e2ceea9ec1510a46be9c978be30a02e43bb125a68b`).
  Evidence: [animation](../experiments/042-connected-fingerings/stepwise-media/strategy-1/trajectory.gif) (SHA256 `4d054f1dbe5fed788441a59874fe236613150e66e8241aca31eac586408f8629`).

## passage-repetition

Repeated C4 with actual index withdrawal and return; duplicate row alternatives.

[connected_passage_search](../experiments/042-connected-fingerings/repetition/result.json).
[passage_media_audit](../experiments/042-connected-fingerings/repetition-media/result.json).
[search_diagram](../experiments/042-connected-fingerings/repetition-media/search.svg).
[animation](../experiments/042-connected-fingerings/repetition-media/strategy-0/trajectory.gif).
- `realization-6ac55b2c814c1b11c5e9`: index r1c5 (C4; release_after_event) → index r1c5 (C4; release_after_event) → index r1c5 (C4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-0`: 54 samples, palm path 27.235 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.016503853853351513}, "index": {"mcp2_abduction_r": 0.021822614442722738, "mcp2_flexion_r": 0.010375523338561843, "md2_flexion_r": 0.03524717796232206, "pm2_flexion_r": 0.016354485717748002}, "middle": {"mcp3_abduction_r": 0.009988140850169774, "mcp3_flexion_r": 0.00402112082734557, "md3_flexion": 0.028932198579163862, "pm3_flexion_r": 0.000432945121735695}, "shoulder": {"elv_angle_r": 0.013618459354740597, "shoulder_elv_r": 0.04250885388939146, "shoulder_rot_r": 0.025596411778209413}, "wrist": {"deviation_r": 0.021778042316751234, "flexion_r": 0.04503716519566703}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.027235164602640624, "sample_count": 54}`.
  Evidence: [connected_passage_search](../experiments/042-connected-fingerings/repetition/result.json) (SHA256 `eea15ef5d31b0946ec0abd7d985e1e0a6a956ff0cb947c490633c3473d62c387`).
  Evidence: [passage_media_audit](../experiments/042-connected-fingerings/repetition-media/result.json) (SHA256 `048ee7598edc8180025ef63a2982dba3635f35cce3c3910f5acfa9f63f0087ae`).
  Evidence: [search_diagram](../experiments/042-connected-fingerings/repetition-media/search.svg) (SHA256 `db4e7431ec8b992044da9c4a105d3efeadaaa95c7a814f9a133e3184fa2cf91a`).
  Evidence: [animation](../experiments/042-connected-fingerings/repetition-media/strategy-0/trajectory.gif) (SHA256 `0b7fee36ab7ccccb5ee4a4e6258995e405b33d2dc515ef05a105c6f59a703ade`).
- `realization-5c85ec07d679bc13cf3b`: index r4c5 (C4; release_after_event) → index r4c5 (C4; release_after_event) → index r4c5 (C4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: not_evaluated; anatomy unresolved.
  Recorded movement `strategy-1`: 47 samples, palm path 27.789 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.009273696884097737}, "index": {"mcp2_abduction_r": 0.01272144256209154, "mcp2_flexion_r": 0.008331461253889172, "md2_flexion_r": 0.02845616185939398, "pm2_flexion_r": 0.021021901228695183}, "middle": {"mcp3_abduction_r": 0.005072353364914711, "mcp3_flexion_r": 0.0065619503597021955, "md3_flexion": 0.011539681591615933, "pm3_flexion_r": 0.0035546710246345814}, "shoulder": {"elv_angle_r": 0.01423410288393695, "shoulder_elv_r": 0.02748920212928474, "shoulder_rot_r": 0.023740551595182}, "wrist": {"deviation_r": 0.02121726145619604, "flexion_r": 0.01955186413743326}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.02778925871507043, "sample_count": 47}`.
  Evidence: [connected_passage_search](../experiments/042-connected-fingerings/repetition/result.json) (SHA256 `eea15ef5d31b0946ec0abd7d985e1e0a6a956ff0cb947c490633c3473d62c387`).
  Evidence: [passage_media_audit](../experiments/042-connected-fingerings/repetition-media/result.json) (SHA256 `048ee7598edc8180025ef63a2982dba3635f35cce3c3910f5acfa9f63f0087ae`).
  Evidence: [search_diagram](../experiments/042-connected-fingerings/repetition-media/search.svg) (SHA256 `db4e7431ec8b992044da9c4a105d3efeadaaa95c7a814f9a133e3184fa2cf91a`).
  Evidence: [animation](../experiments/042-connected-fingerings/repetition-media/strategy-0/trajectory.gif) (SHA256 `0b7fee36ab7ccccb5ee4a4e6258995e405b33d2dc515ef05a105c6f59a703ade`).

## passage-thumb-reversal

Thumb-only C4–Eb4–C4 experimental control, not a universal fingering prior.

[connected_passage_search](../experiments/042-connected-fingerings/thumb-reversal/result.json).
[passage_media_audit](../experiments/042-connected-fingerings/thumb-reversal-media/result.json).
[search_diagram](../experiments/042-connected-fingerings/thumb-reversal-media/search.svg).
[animation](../experiments/042-connected-fingerings/thumb-reversal-media/strategy-0/trajectory.gif).
- `realization-670877f2da16534787a1`: thumb r4c5 (C4; release_after_event) → thumb r4c6 (Eb4; release_after_event) → thumb r1c5 (C4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-0`: 427 samples, palm path 85.274 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.5360420728509341}, "index": {"mcp2_abduction_r": 0.006811830759355542, "mcp2_flexion_r": 0.13566783996682186, "md2_flexion_r": 0.002765660021720323, "pm2_flexion_r": 0.0005428104809107603}, "middle": {"mcp3_abduction_r": 0.11512177378186145, "mcp3_flexion_r": 0.3541679098129035, "md3_flexion": 0.0001703881980210098, "pm3_flexion_r": 0.1824108827646862}, "shoulder": {"elv_angle_r": 0.304406396385973, "shoulder_elv_r": 0.19589815647221484, "shoulder_rot_r": 0.39959049545214226}, "wrist": {"deviation_r": 0.0782917000513309, "flexion_r": 0.29633591438330786}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.08527381220067393, "sample_count": 427}`.
  Evidence: [connected_passage_search](../experiments/042-connected-fingerings/thumb-reversal/result.json) (SHA256 `c305959af1ce30a698c89e3dcb663146f642f20a710a399ebabffe0e84f31c00`).
  Evidence: [passage_media_audit](../experiments/042-connected-fingerings/thumb-reversal-media/result.json) (SHA256 `28950d826a11dc57212451bdfc33bddfb24e30c2885b29600d8779985e45c892`).
  Evidence: [search_diagram](../experiments/042-connected-fingerings/thumb-reversal-media/search.svg) (SHA256 `6abd7b54bc935a2bfa0e834fa497c2c28b78610b17b42e6ba7a3c83993635639`).
  Evidence: [animation](../experiments/042-connected-fingerings/thumb-reversal-media/strategy-0/trajectory.gif) (SHA256 `6a9b34f5c6a1255197838d9ab83228b773a45a15305ca2295fc8af9b82abc77c`).
- `realization-67fe99cb379d89d41860`: thumb r4c5 (C4; release_after_event) → thumb r4c6 (Eb4; release_after_event) → thumb r4c5 (C4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: not_evaluated; anatomy unresolved.
  Recorded movement `strategy-1`: 610 samples, palm path 108.176 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 1.5401759028377455}, "index": {"mcp2_abduction_r": 0.007952420077890543, "mcp2_flexion_r": 0.13566783996682186, "md2_flexion_r": 0.004009069363813955, "pm2_flexion_r": 0.0006205749394165849}, "middle": {"mcp3_abduction_r": 0.14433474331365123, "mcp3_flexion_r": 0.38266210614923163, "md3_flexion": 0.0004608121782161967, "pm3_flexion_r": 0.1824108827646862}, "shoulder": {"elv_angle_r": 0.2543586605039498, "shoulder_elv_r": 0.04819300208591165, "shoulder_rot_r": 0.25093300252509476}, "wrist": {"deviation_r": 0.338424255915902, "flexion_r": 0.29633591438330786}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.10817648971308386, "sample_count": 610}`.
  Evidence: [connected_passage_search](../experiments/042-connected-fingerings/thumb-reversal/result.json) (SHA256 `c305959af1ce30a698c89e3dcb663146f642f20a710a399ebabffe0e84f31c00`).
  Evidence: [passage_media_audit](../experiments/042-connected-fingerings/thumb-reversal-media/result.json) (SHA256 `28950d826a11dc57212451bdfc33bddfb24e30c2885b29600d8779985e45c892`).
  Evidence: [search_diagram](../experiments/042-connected-fingerings/thumb-reversal-media/search.svg) (SHA256 `6abd7b54bc935a2bfa0e834fa497c2c28b78610b17b42e6ba7a3c83993635639`).
  Evidence: [animation](../experiments/042-connected-fingerings/thumb-reversal-media/strategy-0/trajectory.gif) (SHA256 `6a9b34f5c6a1255197838d9ab83228b773a45a15305ca2295fc8af9b82abc77c`).

## passage-held-ring

Held C4 while ring moves E4–F4: contact candidates but finite connected search failed.

[connected_passage_search](../experiments/042-connected-fingerings/held-ring/result.json).
[passage_media_audit](../experiments/042-connected-fingerings/held-ring-media/result.json).
[search_diagram](../experiments/042-connected-fingerings/held-ring-media/search.svg).

## passage-held-repeat

Held C4 with repeated E4 release: finite continuation failure; no successful motion fabricated.

[connected_passage_search](../experiments/042-connected-fingerings/held-repeat/result.json).
[passage_media_audit](../experiments/042-connected-fingerings/held-repeat-media/result.json).
[search_diagram](../experiments/042-connected-fingerings/held-repeat-media/search.svg).

## generated-07ec8d2638eb010f

Distinct generated musical family with an independently sampled model path; anatomy unresolved

[connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-00.json).
[passage_media_audit](../experiments/043-autonomous-discovery/stepwise-media/result.json).
[search_diagram](../experiments/043-autonomous-discovery/stepwise-media/search.svg).
[animation](../experiments/043-autonomous-discovery/stepwise-media/strategy-0/trajectory.gif).
- `realization-602dc0d2bbd53ebb788c`: index r3c5 (D4; release_after_event) → index r4c5 (C4; release_after_event) → index r3c5 (D4; release_after_event) → index r2c6 (E4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-0`: 589 samples, palm path 173.180 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.808563466345413}, "index": {"mcp2_abduction_r": 0.4012153408713779, "mcp2_flexion_r": 0.6976418215544056, "md2_flexion_r": 0.3709880188607027, "pm2_flexion_r": 0.2527128331599296}, "middle": {"mcp3_abduction_r": 0.06423986731101253, "mcp3_flexion_r": 0.13605876216200424, "md3_flexion": 0.055951834913187254, "pm3_flexion_r": 0.06736174093214325}, "shoulder": {"elv_angle_r": 0.783728135955563, "shoulder_elv_r": 0.7740714025526629, "shoulder_rot_r": 0.6464506879955274}, "wrist": {"deviation_r": 0.05491684105119776, "flexion_r": 0.5659087967833465}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.1731797784242307, "sample_count": 589}`.
  Evidence: [connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-00.json) (SHA256 `d98ff8072dc614183ca0b5fee37c4a33aebc8c6a029f10141baf4eacc5c06908`).
  Evidence: [passage_media_audit](../experiments/043-autonomous-discovery/stepwise-media/result.json) (SHA256 `2496b4272498a299c729b23d672c70fa4f35c1e93e0e2420c800d75c0b4c801d`).
  Evidence: [search_diagram](../experiments/043-autonomous-discovery/stepwise-media/search.svg) (SHA256 `e85fb9cf47f9907e8311765432909c8fe9869ba61d31985fe7e5b96efa53e6b4`).
  Evidence: [animation](../experiments/043-autonomous-discovery/stepwise-media/strategy-0/trajectory.gif) (SHA256 `0be01aeef67c58d38e54685566ef2b6138e8f1a052daecc84a9d2622e7f434ae`).
  Evidence: [autonomous_discovery](../experiments/043-autonomous-discovery/discovery/result.json) (SHA256 `153dd6d1b4f97289009543695a26f8fdc47753fcbb72cc91d8be2304fff122bb`).
  Evidence: [generated_search_trial](../experiments/043-autonomous-discovery/discovery/evaluation-00.json) (SHA256 `d98ff8072dc614183ca0b5fee37c4a33aebc8c6a029f10141baf4eacc5c06908`).
  Evidence: [discovery_summary](../experiments/043-autonomous-discovery/summary/result.json) (SHA256 `8e7ff0fc232ad0ef889d352cd9eb755364ec184b99203c6b292786af1125bb23`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/discovery.svg) (SHA256 `813878666a5a815e3b06f6ee32031474a5555e10ed8e89a944df2ba8324b1f99`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/selection.svg) (SHA256 `d1a115b1b421c6022eebbfbb211ad10b0ac368168538c1689c72c2d4f643a0e6`).

## generated-945a2c839056ef55

Distinct generated musical family with an independently sampled model path; anatomy unresolved

[connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-01.json).
[passage_media_audit](../experiments/043-autonomous-discovery/repetition-media/result.json).
[search_diagram](../experiments/043-autonomous-discovery/repetition-media/search.svg).
[animation](../experiments/043-autonomous-discovery/repetition-media/strategy-0/trajectory.gif).
- `realization-662c02c1c5829521c505`: index r3c5 (D4; release_after_event) → index r3c5 (D4; release_after_event) → index r1c6 (Eb4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-0`: 284 samples, palm path 122.132 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.393748661033125}, "index": {"mcp2_abduction_r": 0.013713455761604182, "mcp2_flexion_r": 0.02882109088336704, "md2_flexion_r": 0.24782986510886243, "pm2_flexion_r": 0.41190219833301944}, "middle": {"mcp3_abduction_r": 0.0024040904112902772, "mcp3_flexion_r": 0.0007179130453394966, "md3_flexion": 0.006567112849386839, "pm3_flexion_r": 0.00014280737619504213}, "shoulder": {"elv_angle_r": 0.7246075088276078, "shoulder_elv_r": 0.4141528308940833, "shoulder_rot_r": 0.18385903598178602}, "wrist": {"deviation_r": 0.5779842803101816, "flexion_r": 0.23264154165422068}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.1221320378054508, "sample_count": 284}`.
  Evidence: [connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-01.json) (SHA256 `b362f4fdac0da3ed7c138989a50e698acaa140ccb308a92d17a1761059711946`).
  Evidence: [passage_media_audit](../experiments/043-autonomous-discovery/repetition-media/result.json) (SHA256 `a4fba6d92b54acb98b66e24c66e701e1a48b2e1d98e9a2df1001f639255419f8`).
  Evidence: [search_diagram](../experiments/043-autonomous-discovery/repetition-media/search.svg) (SHA256 `9e5989489d772e01800188a1f014a7c4fba0d11d900b7faf36481420ab97fcb9`).
  Evidence: [animation](../experiments/043-autonomous-discovery/repetition-media/strategy-0/trajectory.gif) (SHA256 `9f0ae2b601bf3f8edb30be52d43af3b84e8a956408f26a486827c4cb47aea161`).
  Evidence: [autonomous_discovery](../experiments/043-autonomous-discovery/discovery/result.json) (SHA256 `153dd6d1b4f97289009543695a26f8fdc47753fcbb72cc91d8be2304fff122bb`).
  Evidence: [generated_search_trial](../experiments/043-autonomous-discovery/discovery/evaluation-01.json) (SHA256 `b362f4fdac0da3ed7c138989a50e698acaa140ccb308a92d17a1761059711946`).
  Evidence: [discovery_summary](../experiments/043-autonomous-discovery/summary/result.json) (SHA256 `8e7ff0fc232ad0ef889d352cd9eb755364ec184b99203c6b292786af1125bb23`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/discovery.svg) (SHA256 `813878666a5a815e3b06f6ee32031474a5555e10ed8e89a944df2ba8324b1f99`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/selection.svg) (SHA256 `d1a115b1b421c6022eebbfbb211ad10b0ac368168538c1689c72c2d4f643a0e6`).

## generated-71ba0dd640884d91

Distinct generated musical family with an independently sampled model path; anatomy unresolved

[connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-02.json).
[passage_media_audit](../experiments/043-autonomous-discovery/reversal-media/result.json).
[search_diagram](../experiments/043-autonomous-discovery/reversal-media/search.svg).
[animation](../experiments/043-autonomous-discovery/reversal-media/strategy-0/trajectory.gif).
- `realization-f3a66ee108aab3fb851c`: index r3c5 (D4; release_after_event) → index r5c6 (E4; release_after_event) → index r5c5 (C#4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-0`: 403 samples, palm path 145.077 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.1227269201105275}, "index": {"mcp2_abduction_r": 0.08381183423827812, "mcp2_flexion_r": 0.34249512138142524, "md2_flexion_r": 0.7273809009214467, "pm2_flexion_r": 0.2666163828761225}, "middle": {"mcp3_abduction_r": 0.06692152554440031, "mcp3_flexion_r": 0.2553452190521265, "md3_flexion": 0.3680300574393137, "pm3_flexion_r": 0.6575391143410134}, "shoulder": {"elv_angle_r": 0.6863481335305959, "shoulder_elv_r": 0.37826378293951723, "shoulder_rot_r": 0.2734370566711858}, "wrist": {"deviation_r": 0.5686758989829698, "flexion_r": 0.18206956383786138}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.1450772200720184, "sample_count": 403}`.
  Evidence: [connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-02.json) (SHA256 `71fc10fa8d19c510e38b7bd738245c5f49c18199de84694c32818a8137a7f85c`).
  Evidence: [passage_media_audit](../experiments/043-autonomous-discovery/reversal-media/result.json) (SHA256 `8b259fd7fce738e9c3e8ece6a1dba2a443d5e7f139217a41ec09d330313b91be`).
  Evidence: [search_diagram](../experiments/043-autonomous-discovery/reversal-media/search.svg) (SHA256 `d70b13bb7042787db97e07ad68296715459a4bf9de4617d962e4f7eb958ab495`).
  Evidence: [animation](../experiments/043-autonomous-discovery/reversal-media/strategy-0/trajectory.gif) (SHA256 `8000a61c14972429ade48aae78f287b09c221f72b079872cacee5d228cc41347`).
  Evidence: [autonomous_discovery](../experiments/043-autonomous-discovery/discovery/result.json) (SHA256 `153dd6d1b4f97289009543695a26f8fdc47753fcbb72cc91d8be2304fff122bb`).
  Evidence: [generated_search_trial](../experiments/043-autonomous-discovery/discovery/evaluation-02.json) (SHA256 `71fc10fa8d19c510e38b7bd738245c5f49c18199de84694c32818a8137a7f85c`).
  Evidence: [discovery_summary](../experiments/043-autonomous-discovery/summary/result.json) (SHA256 `8e7ff0fc232ad0ef889d352cd9eb755364ec184b99203c6b292786af1125bb23`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/discovery.svg) (SHA256 `813878666a5a815e3b06f6ee32031474a5555e10ed8e89a944df2ba8324b1f99`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/selection.svg) (SHA256 `d1a115b1b421c6022eebbfbb211ad10b0ac368168538c1689c72c2d4f643a0e6`).

## generated-dcbc77238f1b5559

Distinct generated musical family with an independently sampled model path; anatomy unresolved

[connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-07.json).
[passage_media_audit](../experiments/043-autonomous-discovery/arpeggio-media/result.json).
[search_diagram](../experiments/043-autonomous-discovery/arpeggio-media/search.svg).
[animation](../experiments/043-autonomous-discovery/arpeggio-media/strategy-0/trajectory.gif).
[animation](../experiments/043-autonomous-discovery/arpeggio-media/strategy-1/trajectory.gif).
- `realization-bd1da87f333184b91a03`: little r4c6 (Eb4; release_after_event) → index r2c7 (G4; release_after_event) → little r2c8 (Bb4; release_after_event) → little r1c6 (Eb4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-0`: 375 samples, palm path 121.677 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.2653318793847302}, "index": {"mcp2_abduction_r": 0.11099205657580996, "mcp2_flexion_r": 0.12739636945995692, "md2_flexion_r": 0.2126730939219852, "pm2_flexion_r": 0.18212647714496644}, "middle": {"mcp3_abduction_r": 0.008361376933952558, "mcp3_flexion_r": 0.0014899725353556825, "md3_flexion": 0.020233409020470626, "pm3_flexion_r": 0.000334330507630598}, "shoulder": {"elv_angle_r": 0.509221677617176, "shoulder_elv_r": 0.1357569559852937, "shoulder_rot_r": 0.13697267904961258}, "wrist": {"deviation_r": 0.11669266542786505, "flexion_r": 0.2561397390799013}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.12167693059276138, "sample_count": 375}`.
  Evidence: [connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-07.json) (SHA256 `034a53238707f86cf74e615e4ded5469a7b194086671d096355e66ce1d49c2f3`).
  Evidence: [passage_media_audit](../experiments/043-autonomous-discovery/arpeggio-media/result.json) (SHA256 `cf4cf70ae27953a182f3c3c7976ca1d4cb6ba6e5f91f2b4809995db96e2380d4`).
  Evidence: [search_diagram](../experiments/043-autonomous-discovery/arpeggio-media/search.svg) (SHA256 `58ad172632d7a824f22d41e7a8292d3e75806141f659b50d0d3f3670e5861c5b`).
  Evidence: [animation](../experiments/043-autonomous-discovery/arpeggio-media/strategy-0/trajectory.gif) (SHA256 `eb21458e39eaa39b82e8cce97dfdc9aa58ebc8dd1a37f14d571751fc0e0a43cd`).
  Evidence: [animation](../experiments/043-autonomous-discovery/arpeggio-media/strategy-1/trajectory.gif) (SHA256 `ef8fb41b525f637e8afe21a0529a344aadc3506b2626925590508658634916e6`).
  Evidence: [autonomous_discovery](../experiments/043-autonomous-discovery/discovery/result.json) (SHA256 `153dd6d1b4f97289009543695a26f8fdc47753fcbb72cc91d8be2304fff122bb`).
  Evidence: [generated_search_trial](../experiments/043-autonomous-discovery/discovery/evaluation-03.json) (SHA256 `4e27f697c7abe688dbfdf8dab9bb73c5da472899740d600643220207117fcb30`).
  Evidence: [generated_search_trial](../experiments/043-autonomous-discovery/discovery/evaluation-07.json) (SHA256 `034a53238707f86cf74e615e4ded5469a7b194086671d096355e66ce1d49c2f3`).
  Evidence: [discovery_summary](../experiments/043-autonomous-discovery/summary/result.json) (SHA256 `8e7ff0fc232ad0ef889d352cd9eb755364ec184b99203c6b292786af1125bb23`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/discovery.svg) (SHA256 `813878666a5a815e3b06f6ee32031474a5555e10ed8e89a944df2ba8324b1f99`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/selection.svg) (SHA256 `d1a115b1b421c6022eebbfbb211ad10b0ac368168538c1689c72c2d4f643a0e6`).
- `realization-79a63b45cc255c2f7a17`: little r4c6 (Eb4; release_after_event) → index r2c7 (G4; release_after_event) → little r2c8 (Bb4; release_after_event) → index r4c6 (Eb4; release_after_event).
  Status: sampled_path_found; quality: numerically_realized; audit: sampled_proxy_constraints_satisfied; anatomy unresolved.
  Recorded movement `strategy-1`: 495 samples, palm path 140.189 mm.
  Descriptors: `{"continuous_validity": null, "joint_excursion_rad": {"forearm": {"pro_sup_r": 0.46287204813280086}, "index": {"mcp2_abduction_r": 0.11805261493075817, "mcp2_flexion_r": 0.27002356938863503, "md2_flexion_r": 0.2126730939219852, "pm2_flexion_r": 0.49535508881305507}, "middle": {"mcp3_abduction_r": 0.10276190129983691, "mcp3_flexion_r": 0.05729957309509667, "md3_flexion": 0.01711750474626466, "pm3_flexion_r": 0.010642274135540808}, "shoulder": {"elv_angle_r": 0.4466083449947672, "shoulder_elv_r": 0.1357569559852937, "shoulder_rot_r": 0.1266986100455501}, "wrist": {"deviation_r": 0.5216443483810062, "flexion_r": 0.19178000403614914}}, "maximum_held_envelope_distance_m": null, "maximum_held_normal_error_rad": null, "maximum_held_position_error_m": null, "maximum_registered_penetration_m": null, "minimum_joint_margin_rad": null, "palm_max_excursion_m": null, "palm_path_length_m": 0.14018940888650386, "sample_count": 495}`.
  Evidence: [connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-07.json) (SHA256 `034a53238707f86cf74e615e4ded5469a7b194086671d096355e66ce1d49c2f3`).
  Evidence: [passage_media_audit](../experiments/043-autonomous-discovery/arpeggio-media/result.json) (SHA256 `cf4cf70ae27953a182f3c3c7976ca1d4cb6ba6e5f91f2b4809995db96e2380d4`).
  Evidence: [search_diagram](../experiments/043-autonomous-discovery/arpeggio-media/search.svg) (SHA256 `58ad172632d7a824f22d41e7a8292d3e75806141f659b50d0d3f3670e5861c5b`).
  Evidence: [animation](../experiments/043-autonomous-discovery/arpeggio-media/strategy-0/trajectory.gif) (SHA256 `eb21458e39eaa39b82e8cce97dfdc9aa58ebc8dd1a37f14d571751fc0e0a43cd`).
  Evidence: [animation](../experiments/043-autonomous-discovery/arpeggio-media/strategy-1/trajectory.gif) (SHA256 `ef8fb41b525f637e8afe21a0529a344aadc3506b2626925590508658634916e6`).
  Evidence: [autonomous_discovery](../experiments/043-autonomous-discovery/discovery/result.json) (SHA256 `153dd6d1b4f97289009543695a26f8fdc47753fcbb72cc91d8be2304fff122bb`).
  Evidence: [generated_search_trial](../experiments/043-autonomous-discovery/discovery/evaluation-03.json) (SHA256 `4e27f697c7abe688dbfdf8dab9bb73c5da472899740d600643220207117fcb30`).
  Evidence: [generated_search_trial](../experiments/043-autonomous-discovery/discovery/evaluation-07.json) (SHA256 `034a53238707f86cf74e615e4ded5469a7b194086671d096355e66ce1d49c2f3`).
  Evidence: [discovery_summary](../experiments/043-autonomous-discovery/summary/result.json) (SHA256 `8e7ff0fc232ad0ef889d352cd9eb755364ec184b99203c6b292786af1125bb23`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/discovery.svg) (SHA256 `813878666a5a815e3b06f6ee32031474a5555e10ed8e89a944df2ba8324b1f99`).
  Evidence: [selection_diagram](../experiments/043-autonomous-discovery/summary/selection.svg) (SHA256 `d1a115b1b421c6022eebbfbb211ad10b0ac368168538c1689c72c2d4f643a0e6`).

## generated-247e3482c25d6082

Preserve an evaluated unsuccessful or proxy-rejected hypothesis; no impossibility claim

[connected_passage_search](../experiments/043-autonomous-discovery/discovery/evaluation-06.json).
[passage_media_audit](../experiments/043-autonomous-discovery/held-media/result.json).
[search_diagram](../experiments/043-autonomous-discovery/held-media/search.svg).

Solver history is not a playing trajectory. A found path establishes one sampled model realization; a finite failure is not impossibility. Rigid proxy overlap does not measure tissue penetration. No result establishes a human movement minimum or universal difficulty.
