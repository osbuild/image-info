"""
Configuration files
"""
import configparser
import contextlib
from typing import Dict
from attr import define
from image_info.report.common import Common
from image_info.utils.files import _read_glob_paths_with_parser


@define(slots=False)
class SystemdLogind(Common):
    """
    SystemdLogind
    """
    flatten = True
    systemd_logind: Dict

    @staticmethod
    def read_logind_config(config_path):
        """
        Read all uncommented key/values from the 'Login" section of system-logind
        configuration file.

        Returns: dictionary with key/values read from the configuration file.
        The returned dictionary may be empty.

        An example return value:
        {
            "NAutoVTs": "0"
        }
        """
        result = {}

        with open(config_path) as f:
            parser = configparser.RawConfigParser()
            # prevent conversion of the option name to lowercase
            parser.optionxform = lambda option: option
            parser.read_file(f)
            with contextlib.suppress(configparser.NoSectionError):
                result.update(parser["Login"])
        return result

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all systemd-logind *.conf files from a predefined list of paths and
        parse them.

        The searched paths are:
        - "/etc/systemd/logind.conf"
        - "/etc/systemd/logind.conf.d/*.conf"
        - "/usr/lib/systemd/logind.conf.d/*.conf"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by 'read_logind_config()'.

        An example return value:
        {
            "/etc/systemd/logind.conf": {
                "NAutoVTs": "0"
            }
        }
        """
        checked_globs = [
            "/etc/systemd/logind.conf",
            "/etc/systemd/logind.conf.d/*.conf",
            "/usr/lib/systemd/logind.conf.d/*.conf"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, SystemdLogind.read_logind_config)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        sdld = json_o.get("systemd-logind")
        if sdld:
            return cls(sdld)
        return None
