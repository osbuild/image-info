"""
Configuration files
"""
import re
import contextlib
from attr import define
from image_info.report.common import Common
from image_info.utils.utils import parse_environment_vars


@define(slots=False)
class Keyboard(Common):
    """
    Keyboard
    """
    flatten = True
    keyboard: dict

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read keyboard configuration for vconsole and X11.

        Returns: dictionary with at most two keys 'X11' and 'vconsole'.
        'vconsole' value is a dictionary representing configuration read from
        /etc/vconsole.conf.
        'X11' value is a dictionary with at most two keys 'layout' and
        'variant', which values are extracted from X11 keyborad configuration.

        An example return value:
        {
            "X11": {
                "layout": "us"
            },
            "vconsole": {
                "FONT": "eurlatgr",
                "KEYMAP": "us"
            }
        }
        """
        result = {}

        # read virtual console configuration
        with contextlib.suppress(FileNotFoundError):
            with open(f"{tree}/etc/vconsole.conf") as f:
                values = parse_environment_vars(f.read())
                if values:
                    result["vconsole"] = values

        # read X11 keyboard configuration
        with contextlib.suppress(FileNotFoundError):
            # Example file content:
            #
            # Section "InputClass"
            #   Identifier "system-keyboard"
            #   MatchIsKeyboard "on"
            #   Option "XkbLayout" "us,sk"
            #   Option "XkbVariant" ",qwerty"
            # EndSection
            x11_config = {}
            match_options_dict = {
                "layout": r'Section\s+"InputClass"\s+.*Option\s+"XkbLayout"\s+"([\w,-]+)"\s+.*EndSection',
                "variant": r'Section\s+"InputClass"\s+.*Option\s+"XkbVariant"\s+"([\w,-]+)"\s+.*EndSection'
            }
            with open(f"{tree}/etc/X11/xorg.conf.d/00-keyboard.conf") as f:
                config = f.read()
                for option, pattern in match_options_dict.items():
                    match = re.search(pattern, config, re.DOTALL)
                    if match and match.group(1):
                        x11_config[option] = match.group(1)

            if x11_config:
                result["X11"] = x11_config

        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        keyboard = json_o.get("keyboard")
        if keyboard:
            return cls(keyboard)
        return None
