"""Named imported digit topology without loading the rendering engine."""

# Finger numbering follows accordion convention; geometry names are imported.
DIGITS = ("thumb", "index", "middle", "ring", "little")
DISTAL_BINDINGS = {
    "thumb": ("distal_thumb_r", "distal_thumb_coll_r", "distal_thumb_coll_2_r", -1),
    "index": ("distph2_r", "distph2_coll_r", "distph2_coll_2_r", 1),
    "middle": ("distph3_r", "distph3_coll_r", "distph3_coll_2_r", 1),
    "ring": ("distph4_r", "distph4_coll_r", "distph4_coll_2_r", 1),
    "little": ("distph5_r", "5distph_coll_r", "5distph_coll_2_r", 1),
}
