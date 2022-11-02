"""
environment
"""
import contextlib
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement


@define(slots=False)
class Hostname(InsideTreeElement):
    """
    Hostname
    """
    flatten = True
    hostname: str = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with contextlib.suppress(FileNotFoundError):
            with open(f"{tree}/etc/hostname") as f:
                return cls(f.read().strip())
        return None

    @classmethod
    def from_json(cls, json_o):
        hostname = json_o.get("hostname")
        if hostname:
            return cls(hostname)
        return None
