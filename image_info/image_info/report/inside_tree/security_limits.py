"""
Configuration files
"""
from typing import Dict
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement
from image_info.utils.files import (_read_glob_paths_with_parser,
                                    read_tmpfilesd_config)


@define(slots=False)
class SecurityLimits(InsideTreeElement):
    """
    SecurityLimits
    """
    flatten = True
    security_limits: Dict = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all security limits *.conf files from a predefined list of paths
        and parse them.

        The searched paths are:
        - "/etc/security/limits.conf"
        - "/etc/security/limits.d/*.conf"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by
        'read_security_limits_config()'.

        An example return value:
        {
            "/etc/security/limits.d": {
                "99-sap.conf": [
                    {
                        "domain": "@sapsys",
                        "item": "nofile",
                        "type": "hard",
                        "value": "65536"
                    },
                    {
                        "domain": "@sapsys",
                        "item": "nofile",
                        "type": "soft",
                        "value": "65536"
                    }
                ]
            }
        }
        """
        checked_globs = [
            "/etc/security/limits.conf",
            "/etc/security/limits.d/*.conf"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, read_tmpfilesd_config)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        sec = json_o.get("security-limits")
        if sec:
            return cls(sec)
        return None
