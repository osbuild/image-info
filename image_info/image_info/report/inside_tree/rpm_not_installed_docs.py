"""
Packages
"""
import os
from typing import List
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.inside_tree_element import InsideTreeElement
from image_info.utils.process import subprocess_check_output


@define(slots=False)
class RpmNotInstalledDocs(InsideTreeElement):
    """
    Read the output of 'rpm --verify'.
    """
    flatten = True
    rpm_not_installed_docs: List = field()

    @classmethod
    def explore(cls, tree, is_ostree=False):
        """
        Gathers information on documentation, which is part of RPM packages,
        but was not installed.

        Returns: list of documentation files, which are normally a part of the
        installed RPM packages, but were not installed (e.g. due to using
        '--excludedocs' option when executing 'rpm' command).
        """
        # check not installed Docs (e.g. when RPMs are installed with
        # --excludedocs)
        not_installed_docs = []
        cmd = ["rpm", "--root", tree, "-qad", "--state"]
        if os.path.exists(os.path.join(tree, "usr/share/rpm")):
            cmd += ["--dbpath", "/usr/share/rpm"]
        elif os.path.exists(os.path.join(tree, "var/lib/rpm")):
            cmd += ["--dbpath", "/var/lib/rpm"]
        output = subprocess_check_output(cmd)
        for line in output.splitlines():
            if line.startswith("not installed"):
                not_installed_docs.append(line.split()[-1])

        if not_installed_docs:
            return cls(not_installed_docs)
        return None

    @classmethod
    def from_json(cls, json_o):
        data = json_o.get("rpm_not_installed_docs")
        if data:
            return cls(data)
        return None
