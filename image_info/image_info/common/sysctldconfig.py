"""
Configuration files
"""
from typing import Dict
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.common import Common
from image_info.utils.files import _read_glob_paths_with_parser


@define(slots=False)
class SysctlDConfig(Common):
    """
    SysctlDConfig
    """
    flatten = True
    sysctl__d: Dict = field()

    @staticmethod
    def read_sysctld_config(config_path):
        """
        Read sysctl configuration file.

        Returns: list of strings representing uncommented lines read from the
        configuration file.

        An example return value:
        [
            "kernel.pid_max = 4194304",
            "vm.max_map_count = 2147483647"
        ]
        """
        values = []

        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # skip comments
                if line[0] in ["#", ";"]:
                    continue
                values.append(line)

        return values

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all sysctl.d *.conf files from a predefined list of paths and parse
        them.

        The searched paths are:
        - "/etc/sysctl.d/*.conf",
        - "/usr/lib/sysctl.d/*.conf"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by 'read_sysctld_config()'.

        An example return value:
        {
            "/etc/sysctl.d": {
                "sap.conf": [
                    "kernel.pid_max = 4194304",
                    "vm.max_map_count = 2147483647"
                ]
            }
        }
        """
        checked_globs = [
            "/etc/sysctl.d/*.conf",
            "/usr/lib/sysctl.d/*.conf"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, SysctlDConfig.read_sysctld_config)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        config = json_o.get("sysctl.d")
        if config:
            return cls(config)
        return None
