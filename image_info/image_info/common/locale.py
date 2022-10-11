"""
environment
"""
import contextlib
from attr import define
from image_info.utils.utils import parse_environment_vars
from image_info.report.common import Common


@define(slots=False)
class Locale(Common):
    """
    Locale
    """
    flatten = True
    locale: str

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all uncommented key/values set in /etc/locale.conf.

        Returns: dictionary with key/values read from the configuration file.
        The returned dictionary may be empty.

        An example return value:
        {
            "LANG": "en_US"
        }
        """
        with contextlib.suppress(FileNotFoundError):
            with open(f"{tree}/etc/locale.conf") as f:
                return cls(parse_environment_vars(f.read()))
        return None

    @classmethod
    def from_json(cls, json_o):
        locale = json_o.get("locale")
        if locale:
            return cls(locale)
        return None
