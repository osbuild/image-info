"""
Configuration files
"""
from attr import define
from image_info.report.common import Common
from image_info.utils.files import(_read_glob_paths_with_parser,
                                   read_tmpfilesd_config)


@define(slots=False)
class Tmpfilesd(Common):
    """
    Tmpfilesd
    """
    flatten = True
    tmpfiles__d: dict

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all tmpfiles.d *.conf files from a predefined list of paths and parse
        them.

        The searched paths are:
        - "/etc/tmpfiles.d/*.conf"
        - "/usr/lib/tmpfiles.d/*.conf"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by 'read_tmpfilesd_config()'.

        An example return value:
        {
            "/etc/tmpfiles.d": {
                "sap.conf": [
                    "x /tmp/.sap*",
                    "x /tmp/.hdb*lock",
                    "x /tmp/.trex*lock"
                ]
            }
        }
        """
        checked_globs = [
            "/etc/tmpfiles.d/*.conf",
            "/usr/lib/tmpfiles.d/*.conf"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, read_tmpfilesd_config)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        tmpf = json_o.get("tmpfiles.d")
        if tmpf:
            return cls(tmpf)
        return None
