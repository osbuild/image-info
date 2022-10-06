"""
Configuration files
"""
from typing import Dict
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field
from image_info.report.common import Common
from image_info.utils.files import (
    _read_glob_paths_with_parser,
    _read_inifile_to_dict)


@define(slots=False)
class YumRepos(Common):
    """
    YumRepos
    """
    flatten = True
    yum_repos: Dict = field()

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all YUM/DNF repo files.

        The searched paths are:
        - "/etc/yum.repos.d/*.repo"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by '_read_inifile_to_dict()'.

        An example return value:
        {
            "/etc/yum.repos.d": {
                "google-cloud.repo": {
                    "google-cloud-sdk": {
                        "baseurl": "https://packages.cloud.google.com/yum/repos/cloud-sdk-el8-x86_64",
                        "enabled": "1",
                        "gpgcheck": "1",
                        "gpgkey": "https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg",
                        "name": "Google Cloud SDK",
                        "repo_gpgcheck": "0"
                    },
                    "google-compute-engine": {
                        "baseurl": "https://packages.cloud.google.com/yum/repos/google-compute-engine-el8-x86_64-stable",
                        "enabled": "1",
                        "gpgcheck": "1",
                        "gpgkey": "https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg",
                        "name": "Google Compute Engine",
                        "repo_gpgcheck": "0"
                    }
                }
            }
        }
        """
        checked_globs = [
            "/etc/yum.repos.d/*.repo"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, _read_inifile_to_dict)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        yum = json_o.get("yum_repos")
        if yum:
            return cls(yum)
        return None
