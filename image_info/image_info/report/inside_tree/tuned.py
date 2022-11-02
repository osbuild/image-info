"""
environment
"""
import contextlib
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement


@define(slots=False)
class Tuned(InsideTreeElement):
    """
    Tuned
    """
    flatten = True
    tuned: str = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read the Tuned active profile and profile mode.

        Returns: dictionary with at most two keys 'active_profile' and
        'profile_mode'. Value of each key is a string representing respective
        tuned configuration value.

        An example return value:
        {
            "active_profile": "sap-hana",
            "profile_mode": "manual"
        }
        """
        result = {}
        config_files = ["active_profile", "profile_mode"]

        with contextlib.suppress(FileNotFoundError):
            for config_file in config_files:
                with open(f"{tree}/etc/tuned/{config_file}") as f:
                    value = f.read()
                    value = value.strip()
                    if value:
                        result[config_file] = value
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        if "tuned" in json_o:
            return cls(json_o["tuned"])
        return None
