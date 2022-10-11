"""
environment
"""
import contextlib
from attr import define
from image_info.report.common import Common


@define(slots=False)
class Hostname(Common):
    """
    Hostname
    """
    flatten = True
    hostname: str

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
