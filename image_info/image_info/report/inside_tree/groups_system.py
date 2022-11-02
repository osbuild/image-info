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
class GroupsSystem(InsideTreeElement):
    """
    Groups
    """
    flatten = True
    groups_system: List[str] = field()

    @classmethod
    def explore(cls, tree, is_ostree=True):
        if not is_ostree:
            return None
        with open(f"{tree}/usr/lib/group") as f:
            return cls(sorted(f.read().strip().split("\n")))

    @classmethod
    def from_json(cls, json_o):
        config = json_o.get("groups-system")
        if config:
            return cls(config)
        return None
