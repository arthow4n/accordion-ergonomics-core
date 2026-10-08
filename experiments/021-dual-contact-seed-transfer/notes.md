# Transfer a constrained dual-contact seed

The missing Bb3 result in 019 might be an initialization artifact. Repeat the
same eight starts from a discovered C4+C#4 pose under the same 16 self-pairs,
geometry, solver and tolerance. Bb3 still has no discovered candidate; C4+E4
has four distinct candidates. This is a useful negative search result, not
an impossibility proof. Another initialization, solver or measured envelope
could change the outcome.

Reproduce: `uv run aec frozen explore
experiments/021-dual-contact-seed-transfer/experiment.json --output artifacts/021`.
The source dual contact is hash-checked. States preserve both finger bindings,
all starts/failures, physical descriptors and reproducible standard/proxy views.
One E4 endpoint supplies the next held-contact experiment.
