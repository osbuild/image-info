"""
Network config
"""

import contextlib
from typing import Dict
import xml.etree.ElementTree
from attr import define
from image_info.report.common import Common
from image_info.common.firewall_default_zone import FirewallDefaultZone


@define(slots=False)
class FirewallEnabled(Common):
    """
    FirewalEnabled
    """
    flatten = True
    firewall_enabled: Dict

    @staticmethod
    def read_firewall_zone(tree):
        """
        Read enabled services from the configuration of the default firewall zone.

        Returns: list of strings representing enabled services in the firewall.
        The returned list may be empty.

        An example return value:
        [
            "ssh",
            "dhcpv6-client",
            "cockpit"
        ]
        """

        default = FirewallDefaultZone.default_zone(tree)
        if default == "":
            default = "public"

        r = []
        try:
            root = xml.etree.ElementTree.parse(
                f"{tree}/etc/firewalld/zones/{default}.xml").getroot()
        except FileNotFoundError:
            root = xml.etree.ElementTree.parse(
                f"{tree}/usr/lib/firewalld/zones/{default}.xml").getroot()

        for element in root.findall("service"):
            r.append(element.get("name"))

        return r

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with contextlib.suppress(FileNotFoundError):
            return cls(FirewallEnabled.read_firewall_zone(tree))
        return None

    @classmethod
    def from_json(cls, json_o):
        fwe = json_o.get("firewall-enabled")
        if fwe or fwe == []:  # legacy requires also empty tables
            return cls(fwe)
        return None
