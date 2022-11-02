"""
environment
"""
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.utils.process import subprocess_check_output
from image_info.report.inside_tree_element import InsideTreeElement


@define(slots=False)
class DefaultTarget(InsideTreeElement):
    """
    Default systemd target
    """
    flatten = True
    default_target: str = field()

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
