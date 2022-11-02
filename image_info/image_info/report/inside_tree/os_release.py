"""
environment
"""
from typing import List
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.utils.utils import parse_environment_vars
from image_info.report.inside_tree_element import InsideTreeElement


@define(slots=False)
class OsRelease(InsideTreeElement):
    """
    Lists the packages of the distribution
    """
    flatten = True
    os_release: List[str] = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with open(f"{tree}/etc/os-release") as f:
            return cls(parse_environment_vars(f.read()))

    @classmethod
    def from_json(cls, json_o):
        return cls(json_o["os-release"])
