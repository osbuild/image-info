"""
environment
"""
import contextlib
from attr import define
from image_info.report.common import Common


@define(slots=False)
class Tuned(Common):
    """
    Tuned
    """
    flatten = True
    tuned: str

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
