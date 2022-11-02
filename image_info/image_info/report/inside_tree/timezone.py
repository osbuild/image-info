"""
environment
"""
import os
import contextlib
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement


@define(slots=False)
class Timezone(InsideTreeElement):
    """
    Timezone
    """
    flatten = True
    timezone: str = field()

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
