"""
environment
"""
import os
import contextlib
from attr import define
from image_info.report.common import Common


@define(slots=False)
class Timezone(Common):
    """
    Timezone
    """
    flatten = True
    timezone: str

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with contextlib.suppress(FileNotFoundError):
            return cls(os.path.basename(os.readlink(f"{tree}/etc/localtime")))
        return None

    @classmethod
    def from_json(cls, json_o):
        timezone = json_o.get("timezone")
        if timezone:
            return cls(timezone)
        return None
