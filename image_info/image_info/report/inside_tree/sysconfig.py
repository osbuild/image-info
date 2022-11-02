"""
Configuration files
"""
import os
import glob
import contextlib
from typing import Dict
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement
from image_info.utils.utils import parse_environment_vars


@define(slots=False)
class Sysconfig(InsideTreeElement):
    """
    Sysconfig
    """
    flatten = True
    sysconfig: Dict = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read selected configuration files from /etc/sysconfig.

        Currently supported sysconfig files are:
        - 'kernel' - /etc/sysconfig/kernel
        - 'network' - /etc/sysconfig/network
        - 'network-scripts' - /etc/sysconfig/network-scripts/ifcfg-*

        Returns: dictionary with the keys being the supported types of sysconfig
        configurations read by the function. Values of 'kernel' and 'network' keys
        are a dictionaries containing key/values read from the respective
        configuration files. Value of 'network-scripts' key is a dictionary with
        the keys corresponding to the suffix of each 'ifcfg-*' configuration file
        and their values holding dictionaries with all key/values read from the
        configuration file.
        The returned dictionary may be empty.

        An example return value:
        {
            "kernel": {
                "DEFAULTKERNEL": "kernel",
                "UPDATEDEFAULT": "yes"
            },
            "network": {
                "NETWORKING": "yes",
                "NOZEROCONF": "yes"
            },
            "network-scripts": {
                "ens3": {
                    "BOOTPROTO": "dhcp",
                    "BROWSER_ONLY": "no",
                    "DEFROUTE": "yes",
                    "DEVICE": "ens3",
                    "IPV4_FAILURE_FATAL": "no",
                    "IPV6INIT": "yes",
                    "IPV6_AUTOCONF": "yes",
                    "IPV6_DEFROUTE": "yes",
                    "IPV6_FAILURE_FATAL": "no",
                    "NAME": "ens3",
                    "ONBOOT": "yes",
                    "PROXY_METHOD": "none",
                    "TYPE": "Ethernet",
                    "UUID": "106f1b31-7093-41d6-ae47-1201710d0447"
                },
                "eth0": {
                    "BOOTPROTO": "dhcp",
                    "DEVICE": "eth0",
                    "IPV6INIT": "no",
                    "ONBOOT": "yes",
                    "PEERDNS": "yes",
                    "TYPE": "Ethernet",
                    "USERCTL": "yes"
                }
            }
        }
        """
        result = {}
        sysconfig_paths = {
            "kernel": f"{tree}/etc/sysconfig/kernel",
            "network": f"{tree}/etc/sysconfig/network"
        }
        # iterate through supported configs
        for name, path in sysconfig_paths.items():
            with contextlib.suppress(FileNotFoundError):
                with open(path) as f:
                    # if file exists start with empty array of values
                    result[name] = parse_environment_vars(f.read())

        # iterate through all files in /etc/sysconfig/network-scripts
        network_scripts = {}
        files = glob.glob(f"{tree}/etc/sysconfig/network-scripts/ifcfg-*")
        for file in files:
            ifname = os.path.basename(file).lstrip("ifcfg-")
            with open(file) as f:
                network_scripts[ifname] = parse_environment_vars(f.read())

        if network_scripts:
            result["network-scripts"] = network_scripts

        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        config = json_o.get("sysconfig")
        if config:
            return cls(config)
        return None
