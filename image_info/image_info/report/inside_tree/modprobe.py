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
from image_info.utils.files import _read_glob_paths_with_parser


@define(slots=False)
class Modprobe(InsideTreeElement):
    """
    Modprobe
    """
    flatten = True
    modprobe: Dict = field()

    @staticmethod
    def read_modprobe_config(config_path):
        """
        Read a specific modprobe configuragion file and for now, extract only
        blacklisted kernel modules.

        Returns: dictionary with the keys corresponding to specific modprobe
        commands and values being the values of these commands.

        An example return value:
        {
            "blacklist": [
                "nouveau"
            ]
        }
        """
        file_result = {}

        BLACKLIST_CMD = "blacklist"

        with open(config_path) as f:
            # The format of files under modprobe.d: one command per line,
            # with blank lines and lines starting with '#' ignored.
            # A '\' at the end of a line causes it to continue on the next line.
            line_to_be_continued = ""
            for line in f:
                line = line.strip()
                # line is not blank
                if line:
                    # comment, skip it
                    if line[0] == "#":
                        continue
                    # this line continues on the following line
                    if line[-1] == "\\":
                        line_to_be_continued += line[:-1]
                        continue
                    # this line ends here
                    else:
                        # is this line continuation of the previous one?
                        if line_to_be_continued:
                            line = line_to_be_continued + line
                            line_to_be_continued = ""
                        cmd, cmd_args = line.split(' ', 1)
                        # we care only about blacklist command for now
                        if cmd == BLACKLIST_CMD:
                            modules_list = file_result[BLACKLIST_CMD] = []
                            modules_list.append(cmd_args)

        return file_result

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all modprobe *.conf files from a predefined list of paths and extract
        supported commands. For now, extract only blacklisted kernel modules.

        The searched paths are:
        - "/etc/modprobe.d/*.conf"
        - "/usr/lib/modprobe.d/*.conf"
        - "/usr/local/lib/modprobe.d/*.conf"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by 'read_modprobe_config()'.

        An example return value:
        {
            "/usr/lib/modprobe.d": {
                "blacklist-nouveau.conf": {
                    "blacklist": [
                        "nouveau"
                    ]
                }
            }
        }
        """
        checked_globs = [
            "/etc/modprobe.d/*.conf",
            "/usr/lib/modprobe.d/*.conf",
            "/usr/local/lib/modprobe.d/*.conf"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, Modprobe.read_modprobe_config)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        modprobe = json_o.get("modprobe")
        if modprobe:
            return cls(modprobe)
        return None
