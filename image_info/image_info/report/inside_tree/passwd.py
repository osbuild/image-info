"""
Users
"""
from typing import List
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement


@define(slots=False)
class Passwd(InsideTreeElement):
    """
    Passwd
    """
    flatten = True
    passwd: List[str] = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with open(f"{tree}/etc/passwd") as f:
            return cls(sorted(f.read().strip().split("\n")))

    @classmethod
    def from_json(cls, json_o):
        return cls(json_o["passwd"])
