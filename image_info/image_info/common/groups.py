"""
Users
"""
from attr import define
from image_info.report.common import Common


@define(slots=False)
class Groups(Common):
    """
    Groups
    """
    flatten = True
    groups: list[str]

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with open(f"{tree}/etc/group") as f:
            return cls(sorted(f.read().strip().split("\n")))

    @classmethod
    def from_json(cls, json_o):
        return cls(json_o["groups"])
