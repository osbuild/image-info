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
class MachineId(Common):
    """
    MachineId
    """
    flatten = True
    machine_id: str = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all uncommented key/values set in /etc/locale.conf.

        Returns: dictionary with key/values read from the configuration file.
        The returned dictionary may be empty.

        An example return value:
        {
            "LANG": "en_US"
        }
        """
        with contextlib.suppress(FileNotFoundError):
            with open(f"{tree}/etc/machine-id") as f:
                return cls(f.readline())
        return cls("")  # in the legacy image-info the value exists even empty

    @classmethod
    def from_json(cls, json_o):
        machine_id = json_o.get("machine-id")
        if machine_id:
            return cls(machine_id)
        return cls("")  # in the legacy image-info the value exists even empty
