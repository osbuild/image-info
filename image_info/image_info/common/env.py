"""
environment
"""
import os
import contextlib
from attr import define
from image_info.utils.process import subprocess_check_output
from image_info.utils.utils import parse_environment_vars
from image_info.report.common import Common


@define(slots=False)
class OsRelease(Common):
    """
    Lists the packages of the distribution
    """
    flatten = True
    os_release: list[str]

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with open(f"{tree}/etc/os-release") as f:
            return cls(parse_environment_vars(f.read()))

    @classmethod
    def from_json(cls, json_o):
        return cls(json_o["os-release"])


@define(slots=False)
class DefaultTarget(Common):
    """
    Default systemd target
    """
    flatten = True
    default_target: str

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read the default systemd target.

        Returns: string representing the default systemd target.

        An example return value:
        "multi-user.target"
        """
        default_target = subprocess_check_output(
            ["systemctl", f"--root={tree}", "get-default"]).rstrip()
        if default_target:
            return cls(default_target)
        return None

    @classmethod
    def from_json(cls, json_o):
        default_target = json_o.get("default-target")
        if default_target:
            return cls(default_target)
        return None


@define(slots=False)
class Hostname(Common):
    """
    Hostname
    """
    flatten = True
    hostname: str

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with contextlib.suppress(FileNotFoundError):
            with open(f"{tree}/etc/hostname") as f:
                return cls(f.read().strip())
        return None

    @classmethod
    def from_json(cls, json_o):
        hostname = json_o.get("hostname")
        if hostname:
            return cls(hostname)
        return None


@define(slots=False)
class Timezone(Common):
    """
    Timezone
    """
    flatten = True
    timezone: str

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        with contextlib.suppress(FileNotFoundError):
            return cls(os.path.basename(os.readlink(f"{tree}/etc/localtime")))
        return None

    @classmethod
    def from_json(cls, json_o):
        timezone = json_o.get("timezone")
        if timezone:
            return cls(timezone)
        return None
