"""
Configuration files
"""
from attr import define
from image_info.report.common import Common
from image_info.utils.files import _read_glob_paths_with_parser


@define(slots=False)
class Dracut(Common):
    """
    Dracut
    """
    flatten = True
    dracut: dict

    @staticmethod
    def read_dracut_config(config_path):
        """
        Read specific dracut configuration file.

        Returns: dictionary representing the uncommented configuration options
        read from the file.

        An example return value:
        {
            "install_items": " sgdisk "
            "add_drivers": " xen-netfront xen-blkfront "
        }
        """
        result = {}

        with open(config_path) as f:
            # dracut configuration key/values delimiter is '=' or '+='
            for line in f:
                line = line.strip()
                # A '#' indicates the beginning of a comment; following
                # characters, up to the end of the line are not interpreted.
                line_comment = line.split("#", 1)
                line = line_comment[0]
                if line:
                    key, value = line.split("=", 1)
                    if key[-1] == "+":
                        key = key[:-1]
                    result[key] = value.strip('"')

        return result

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all dracut *.conf files from a predefined list of paths and parse
        them.

        The searched paths are:
        - "/etc/dracut.conf.d/*.conf"
        - "/usr/lib/dracut/dracut.conf.d/*.conf"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by 'read_dracut_config()'.

        An example return value:
        {
            "/etc/dracut.conf.d": {
                "sgdisk.conf": {
                    "install_items": " sgdisk "
                },
            },
            "/usr/lib/dracut/dracut.conf.d": {
                "xen.conf": {
                    "add_drivers": " xen-netfront xen-blkfront "
                }
            }
        }
        """
        checked_globs = [
            "/etc/dracut.conf.d/*.conf",
            "/usr/lib/dracut/dracut.conf.d/*.conf"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, Dracut.read_dracut_config)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        dracut = json_o.get("dracut")
        if dracut:
            return cls(dracut)
        return None
