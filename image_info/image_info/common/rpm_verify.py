"""
Packages
"""
import subprocess
from attr import define
from image_info.report.common import Common


@define(slots=False)
class RpmVerify(Common):
    """
    Read the output of 'rpm --verify'.
    """
    changed: dict
    missing: list

    @classmethod
    def explore(cls, tree, is_ostree=False):
        """
        Read the output of 'rpm --verify'.

        Returns: dictionary with two keys 'changed' and 'missing'.
        - 'changed' value is a dictionary with the keys representing modified
          files from installed RPM packages and values representing types of
          applied modifications.
        - 'missing' value is a list of strings prepresenting missing values
          owned by installed RPM packages.
        """
        if is_ostree:
            return None
        # cannot use `rpm --root` here, because rpm uses passwd from the host to
        # verify user and group ownership:
        #   https://github.com/rpm-software-management/rpm/issues/882
        rpm = subprocess.Popen(["chroot", tree, "rpm", "--verify", "--all"],
                               stdout=subprocess.PIPE, encoding="utf-8")

        changed = {}
        missing = []
        for line in rpm.stdout:
            # format description in rpm(8), under `--verify`
            attrs = line[:9]
            if attrs == "missing  ":
                missing.append(line[12:].rstrip())
            else:
                changed[line[13:].rstrip()] = attrs

        # ignore return value, because it returns non-zero when it found changes
        rpm.wait()
        return cls(changed, sorted(missing))

    @classmethod
    def from_json(cls, json_o):
        return cls(json_o["changed"], json_o["missing"])
