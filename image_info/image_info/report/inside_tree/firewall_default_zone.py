"""
Network config
"""

try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement
from image_info.utils.utils import parse_environment_vars


@define(slots=False)
class FirewallDefaultZone(InsideTreeElement):
    """
    FirewallDefaultZone
    """
    flatten = True
    firewall_default_zone: str = field()

    @staticmethod
    def default_zone(tree):
        """
        Read the name of the default firewall zone

        Returns: a string with the zone name. If the firewall configuration doesn't
        exist, an empty string is returned.

        An example return value:
        "trusted"
        """
        try:
            with open(f"{tree}/etc/firewalld/firewalld.conf") as f:
                conf = parse_environment_vars(f.read())
                return conf["DefaultZone"]
        except FileNotFoundError:
            return ""

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        zone = FirewallDefaultZone.default_zone(tree)
        if zone:
            return cls(zone)
        else:
            return None

    @classmethod
    def from_json(cls, json_o):
        zone = json_o.get("firewall-default-zone")
        if zone:
            return cls(zone)
        return None
