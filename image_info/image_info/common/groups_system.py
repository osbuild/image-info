"""
Users
"""
from attr import define
from image_info.report.common import Common


@define(slots=False)
class GroupsSystem(Common):
    """
    Groups
    """
    flatten = True
    groups_system: list[str]

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
