"""
Users
"""
from attr import define
from image_info.report.common import Common


@define(slots=False)
class PasswdSystem(Common):
    """
    Passwd
    """
    flatten = True
    passwd_system: list[str]

    @classmethod
    def explore(cls, tree, is_ostree=False):
        if not is_ostree:
            return None
        with open(f"{tree}/usr/lib/passwd") as f:
            return cls(sorted(f.read().strip().split("\n")))

    @classmethod
    def from_json(cls, json_o):
        config = json_o.get("passwd-system")
        if config:
            return cls(config)
        return None
