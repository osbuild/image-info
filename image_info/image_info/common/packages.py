"""
Packages
"""
import os
from typing import List
import subprocess
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.common import Common
from image_info.utils.process import subprocess_check_output


@define(slots=False)
class Packages(Common):
    """
    Lists the packages of the distribution
    """
    flatten = True
    packages: List[str] = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read NVRs of RPM packages installed on the system.

        Returns: sorted list of strings representing RPM packages installed
        on the system.
        """
        cmd = ["rpm", "--root", tree, "-qa"]
        if os.path.exists(os.path.join(tree, "usr/share/rpm")):
            cmd += ["--dbpath", "/usr/share/rpm"]
        elif os.path.exists(os.path.join(tree, "var/lib/rpm")):
            cmd += ["--dbpath", "/var/lib/rpm"]
        packages = subprocess_check_output(cmd, str.split)
        return cls(list(sorted(packages)))

    @classmethod
    def from_json(cls, json_o):
        return cls(json_o["packages"])
