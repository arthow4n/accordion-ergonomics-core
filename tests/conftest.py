"""All canonical physical tests are headless, including diagnostic rendering."""

import os

os.environ.setdefault("MUJOCO_GL", "egl")
