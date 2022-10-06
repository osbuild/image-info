"""
Configuration files
"""
import contextlib
from typing import List
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.common import Common


@define(slots=False)
class Authselect(Common):
    """
    AuthSelect
    """
    enabled_features: List = field()
    profile_id: str = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read authselect configuration.

        Returns: dictionary with two keys 'profile-id' and 'enabled-features'.
        - 'profile-id' value is a string representing the configured authselect
          profile.
        - 'enabled-features' value is a list of strings representing enabled
          features of the used authselect profile. In case there are no specific
          features enabled, the list is empty.
        """
        with contextlib.suppress(FileNotFoundError):
            #pylint: disable = unspecified-encoding
            with open(f"{tree}/etc/authselect/authselect.conf") as f:
                # the first line is always the profile ID
                # following lines are listing enabled features
                # lines starting with '#' and empty lines are skipped
                authselect_conf_lines = []
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line[0] == "#":
                        continue
                    authselect_conf_lines.append(line)
                if authselect_conf_lines:
                    return cls(authselect_conf_lines[1:],
                               authselect_conf_lines[0])
        return None

    @classmethod
    def from_json(cls, json_o):
        return cls(json_o["enabled-features"], json_o["profile-id"])
