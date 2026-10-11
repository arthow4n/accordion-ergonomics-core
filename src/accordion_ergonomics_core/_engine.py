"""Boundary for MuJoCo's untyped pybind API.

MuJoCo 3.15 exports native symbols via wildcard imports without type stubs.
Ty cannot resolve even MjModel/mj_forward. Keep this uncertainty at the engine
boundary; project-owned geometry and experiment parameters remain typed.
"""

import os
from importlib import import_module
from typing import Any

os.environ.setdefault("MUJOCO_GL", "egl")
mujoco: Any = import_module("mujoco")
type Model = Any
type Data = Any
type Spec = Any
