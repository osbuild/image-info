"""
Configuration files
"""
import os
import glob
from typing import Dict
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.common import Common


@define(slots=False)
class Udev(Common):
    flatten = True
    _l_etc_l_udev_l_rules__d: Dict = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read udev rules defined in /etc/udev/rules.d.

        Returns: dictionary with the keys representing names of files with udev
        rules from /etc/udev/rules.d. Value of each key is a list of strings
        representing uncommented lines read from the configuration file. If
        the file is empty (e.g. because of masking udev configuration installed
        by an RPM), an emptu list is returned as the respective value.

        An example return value:
        {
            "80-net-name-slot.rules": []
        }
        """
        result = {}

        for file in glob.glob(f"{tree}/etc/udev/rules.d/*.rules"):
            with open(file) as f:
                lines = []
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line[0] == "#":
                        continue
                    lines.append(line)
                # include also empty files in the report
                result[os.path.basename(file)] = lines
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        config = json_o.get("/etc/udev/rules.d")
        if config:
            return cls(config)
        return None
