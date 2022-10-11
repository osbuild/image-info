"""
Configuration files
"""
from attr import define
from image_info.report.common import Common
from image_info.utils.files import _read_inifile_to_dict


@define(slots=False)
class AutomaticDnf(Common):
    """
    AutomaticDnf
    """
    flatten = True
    _l_etc_l_dnf_l_automatic__conf: dict

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read DNF Automatic configuation.

        Returns: dictionary as returned by '_read_inifile_to_dict()'.

        An example return value:
        {
            "base": {
                "debuglevel": "1"
            },
            "command_email": {
                "email_from": "root@example.com",
                "email_to": "root"
            },
            "commands": {
                "apply_updates": "yes",
                "download_updates": "yes",
                "network_online_timeout": "60",
                "random_sleep": "0",
                "upgrade_type": "security"
            },
            "email": {
                "email_from": "root@example.com",
                "email_host": "localhost",
                "email_to": "root"
            },
            "emitters": {
                "emit_via": "stdio"
            }
        }
        """
        result = _read_inifile_to_dict(f"{tree}/etc/dnf/automatic.conf")
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        conf = json_o.get("/etc/dnf/automatic.conf")
        if conf:
            return cls(conf)
        return None
