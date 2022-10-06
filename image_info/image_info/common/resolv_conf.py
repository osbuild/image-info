"""
Network config
"""

import contextlib
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.common import Common


@define(slots=False)
class ResolvConf(Common):
    """
    ResolvConf
    """
    flatten = True
    _l_etc_l_resolv__conf: str = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read /etc/resolv.conf.

        Returns: a list of uncommented lines from the /etc/resolv.conf.

        An example return value:
        [
            "search redhat.com",
            "nameserver 192.168.1.1",
            "nameserver 192.168.1.2"
        ]
        """
        result = []

        with contextlib.suppress(FileNotFoundError):
            with open(f"{tree}/resolv.conf") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line[0] == "#":
                        continue
                    result.append(line)

        if result:
            return cls(result)
        return cls([])   # The legacy requires even an empty resolvonf array

    @classmethod
    def from_json(cls, json_o):
        resolv = json_o.get("/etc/resolv.conf")
        return cls(resolv)  # The legacy requires even an empty resolvonf array
