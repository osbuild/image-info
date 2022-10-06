"""
Configuration files
"""
import contextlib
from typing import Dict
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.common import Common


@define(slots=False)
class Chrony(Common):
    """
    Chrony
    """
    flatten = True
    chrony: Dict = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read specific directives from Chrony configuration. Currently parsed
        directives are:
        - 'server'
        - 'pool'
        - 'peer'
        - 'leapsectz'

        Returns: dictionary with the keys representing parsed directives from
        Chrony configuration. Value of each key is a list of strings containing
        arguments provided with each occurance of the directive in the
        configuration.
        """
        chrony = {}
        parsed_directives = ["server", "pool", "peer", "leapsectz"]
        with contextlib.suppress(FileNotFoundError):
            #pylint: disable = unspecified-encoding
            with open(f"{tree}/etc/chrony.conf") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # skip comments
                    if line[0] in ["!", ";", "#", "%"]:
                        continue
                    split_line = line.split()
                    if split_line[0] in parsed_directives:
                        try:
                            directive_list = chrony[split_line[0]]
                        except KeyError:
                            directive_list = chrony[split_line[0]] = []
                        directive_list.append(" ".join(split_line[1:]))
        if chrony:
            return cls(chrony)
        return None

    @classmethod
    def from_json(cls, json_o):
        chrony = json_o.get("chrony")
        if chrony:
            return cls(chrony)
        return None
