"""
environment
"""
import os
import glob
import contextlib
from typing import List
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.utils.utils import parse_environment_vars
from image_info.report.common import Common


@define(slots=False)
class BootEnvironment(Common):
    """
    BootEnvironment
    """
    flatten = True
    boot_environment: List[str] = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        if os.path.exists(f"{tree}/boot") and len(os.listdir(f"{tree}/boot")) > 0:
            with contextlib.suppress(FileNotFoundError):
                with open(f"{tree}/boot/grub2/grubenv") as f:
                    return cls(parse_environment_vars(f.read()))
        return None

    @classmethod
    def from_json(cls, json_o):
        config = json_o.get("boot-environment")
        if config:
            return cls(config)
        return None
