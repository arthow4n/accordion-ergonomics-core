# Ground the local keyboard slope using construction sections

The owner challenged the angle of the keyboard against the case/grille and
requested sources beyond perspective product pictures. Review the source table
in [generic-cba.md](../../docs/research/generic-cba.md#construction-sections-and-the-angle-revision-034).
Pascher's directly drawn section, historical bayan repair sections (figs25,66,70)
and Hohner's flat/stepped grip description distinguish board, case, grille and
mechanism. They establish shallow rearward or near-forward keyboard structures;
they provide no measured universal five-row angle. We choose 20 degrees for this
one flat reference, explicitly as engineering judgment. No oblique product
photograph was used for angle or dimension metrology. A 30-degree local trial
remained transient and was superseded before publication.

`generic_cba_v2` changes B origin to H=(78,100,-160) mm and board tilt to 20 degrees.
The case shoulder and rear return follow the board; return joins backing's back
edge instead of crossing the panel underside. The 12 mm board, 4 mm released
caps, finite musical layout and all anatomy/collision masks remain unchanged.
V1 is a retired, explicitly rejected selector in current code; reproduce its
frozen worlds with archived source. `rectangular_v0` identities remain exact.

A separate mounting bug applied seated yaw to H, although the canonical contract
specifies B. Now R_WH=R_WB R_HB^T. At B yaw -30 degrees, H yaw is -10 degrees;
button normals are 30 degrees toward the right from forward. This is independent
of the local angle correction. A temporary corrected-mount/55-degree run remains
in artifacts only; it did not resolve the owner's local-angle concern.

Numerical audit: target-frame error <=1.20e-16 m; nonparent component cap clearance
>=5.5 mm; intentional primitive seams overlap <=6.01 mm. Neutral anatomical
proxy/component minimum 10.842 mm; approximate thigh distances 11.840 and
11.275 mm. Support envelopes are approximate and no load equilibrium is solved.
Neutral imported humerus/thorax overlap remains, independently of instrument
clearance; skeletal pictures do not certify human tissue feasibility.

Instrument views use orthographic projection; the end section is exactly top-on.
Body views retain perspective. Saved-state replay and frame tests accompany
`reference/`. The 12 mm board, 6 mm backing and 4 mm caps remain distinct in the
metric cross-section. The body stays in its prescribed neutral pose here;
playing-state comparisons are separately frozen in 035. Additional diagnostic
keys preserve every unnamed imported collision surface instead of overwriting
them in an empty-name dictionary entry. This improves reporting, not filtering.
