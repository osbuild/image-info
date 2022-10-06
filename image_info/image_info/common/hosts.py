"""
Network config
"""

from typing import List
import contextlib
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.common import Common


@define(slots=False)
class Hosts(Common):
    """
    Hosts
    """
    flatten = True
    hosts: List[str] = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read non-empty lines of /etc/hosts.

        Returns: list of strings for all uncommented lines in the configuration file.
        The returned list may be empty.

        An example return value:
        [
            "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4",
            "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6"
        ]
        """
        result = []

        with contextlib.suppress(FileNotFoundError):
            with open(f"{tree}/etc/hosts") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        result.append(line)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        hosts = json_o.get("hosts")
        if hosts:
            return cls(hosts)
        return None
