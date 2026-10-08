# A finite index-action atlas from recorded C4

The reproducible full-board query explores all 62 physical buttons with index
contact, three deterministic starts per target, endpoint deduplication and
independent withdrawal/RRT path search. It discovers sampled transitions for
29 buttons; 33 have no accepted pose found. These are finite-search outcomes,
not a 29-button human reachability boundary. Other fingers remain present and
frozen; only the source index contact may release.

![Discovered palm relocation in millimetres; X is search failure](atlas.png)

Each circle reports the best discovered accepted-path endpoint palm displacement.
The source is outlined orange. Nothing here is a comfort score, a proof of
minimal movement or proof of physical impossibility. The same pitch may have
several physical buttons. Ranking uses physical palm movement, not MIDI distance.

Largest discovered-best relocation: r2c15/G6, 300.29 mm. A finer audit and render
are needed before using it as a demanding model exercise. Small and large motions
coexist; local initialization changes which configuration is discovered.

The frozen run took approximately 213 s on this environment. Per-action records
preserve all starts, rejected candidates, accepted alternatives, complete sampled
paths and numerical budgets. The compact index references those files by hash.
The executed package source is archived; recorded uv lock/package/anatomy hashes
remain required to reproduce the environment.

```sh
uv run aec frozen atlas experiments/007-index-atlas/experiment.json --output artifacts/atlas
uv run aec atlas-render artifacts/atlas/result.json --output artifacts/atlas/atlas.png
```

Current exclusions: tempo, depression, force, individualized physiology,
complete self-collision, instrument shell/straps, held contacts and continuous
collision certification.

Measured computational cost: candidate discovery accounts for about 189 of
213 s; endpoint solves dominate this run, rather than the small RRT bridges.
No caching or approximation was introduced to speed up the first atlas.
