"""
Configuration files
"""
import glob
import configparser
from typing import Dict
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement
from image_info.utils.files import _read_glob_paths_with_parser


@define(slots=False)
class SystemdServiceDropins(InsideTreeElement):
    """
    SystemdServiceDropins
    """
    flatten = True
    systemd_service_dropins: Dict = field()

    @staticmethod
    def read_systemd_service_dropin(dropin_dir_path):
        """
        Read systemd .service unit drop-in configurations.

        Returns: dictionary representing the combined drop-in configurations.

        An example return value:
        {
            "Service": {
                "Environment": "NM_CLOUD_SETUP_EC2=yes"
            }
        }
        """
        # read all unit drop-in configurations
        config_files = glob.glob(f"{dropin_dir_path}/*.conf")
        parser = configparser.RawConfigParser()
        # prevent conversion of the opion name to lowercase
        parser.optionxform = lambda option: option
        parser.read(config_files)

        dropin_config = {}
        for section in parser.sections():
            section_config = {}
            section_config.update(parser[section])
            if section_config:
                dropin_config[section] = section_config

        return dropin_config

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all systemd .service unit config files from a predefined list of
        paths and parse them.

        The searched paths are:
        - "/etc/systemd/system/*.service.d"
        - "/usr/lib/systemd/system/*.service.d"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by
        'read_systemd_service_dropin()'.

        An example return value:
        {
            "/etc/systemd/system": {
                "nm-cloud-setup.service.d": {
                    "Service": {
                        "Environment": "NM_CLOUD_SETUP_EC2=yes"
                    }
                }
            }
        }
        """
        checked_globs = [
            "/etc/systemd/system/*.service.d",
            "/usr/lib/systemd/system/*.service.d"
        ]

        result = _read_glob_paths_with_parser(
            tree,
            checked_globs,
            SystemdServiceDropins.read_systemd_service_dropin)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        config = json_o.get("systemd-service-dropins")
        if config:
            return cls(config)
        return None
