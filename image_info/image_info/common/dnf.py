"""
Configuration files
"""
import os
import glob
from attr import define
from image_info.report.common import Common
from image_info.utils.files import _read_inifile_to_dict


@define(slots=False)
class Dnf(Common):
    """
    Dnf
    """
    flatten = True
    dnf: dict

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read DNF configuration and defined variable files.

        Returns: dictionary with at most two keys 'dnf.conf' and 'vars'.
        'dnf.conf' value is a dictionary representing the DNF configuration
        file content.
        'vars' value is a dictionary which keys represent names of files from
        /etc/dnf/vars/ and values are strings representing the file content.

        An example return value:
        {
            "dnf.conf": {
                "main": {
                    "installonly_limit": "3"
                }
            },
            "vars": {
                "releasever": "8.4"
            }
        }
        """
        result = {}

        dnf_config = _read_inifile_to_dict(f"{tree}/etc/dnf/dnf.conf")
        if dnf_config:
            result["dnf.conf"] = dnf_config

        dnf_vars = {}
        for file in glob.glob(f"{tree}/etc/dnf/vars/*"):
            with open(file) as f:
                dnf_vars[os.path.basename(file)] = f.read().strip()
        if dnf_vars:
            result["vars"] = dnf_vars

        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        dnf = json_o.get("dnf")
        if dnf:
            return cls(dnf)
        return None
