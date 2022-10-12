"""
environment
"""
import os
import glob
import contextlib
from attr import define
from image_info.utils.utils import parse_environment_vars
from image_info.report.common import Common


@define(slots=False)
class BootEnvironment(Common):
    """
    BootEnvironment
    """
    flatten = True
    boot_environment: list[str]

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
