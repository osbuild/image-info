"""
Configuration files
"""
import configparser
import os
import glob
import contextlib
from attr import define
from image_info.report.common import Common


def _read_glob_paths_with_parser(tree, glob_paths, parser_func):
    """
    Use 'parser_func' to read all files obtained by using all 'glob_paths'
    globbing patterns under the 'tree' path.

    The 'glob_paths' is a list string patterns accepted by glob.glob().
    The 'parser_func' function is expected to take a single string argument
    containing the absolute path to a configuration file which should be parsed.
    Its return value can be arbitrary representation of the parsed
    configuration.

    Returns: dictionary with the keys corresponding to directories, which
    contain configuration files mathing the provided glob pattern. Value of
    each key is another dictionary with keys representing each filename and
    values being the parsed configuration representation as returned by the
    provided 'parser_func' function.

    An example return value for dracut configuration paths and parser:
    {
        "/etc/dracut.conf.d": {
            "sgdisk.conf": {
                "install_items": " sgdisk "
            },
        },
        "/usr/lib/dracut/dracut.conf.d": {
            "xen.conf": {
                "add_drivers": " xen-netfront xen-blkfront "
            }
        }
    }
    """
    result = {}

    for glob_path in glob_paths:
        glob_path_result = {}

        files = glob.glob(f"{tree}{glob_path}")
        for file in files:
            config = parser_func(file)
            if config:
                filename = os.path.basename(file)
                glob_path_result[filename] = config

        if glob_path_result:
            checked_path = os.path.dirname(glob_path)
            result[checked_path] = glob_path_result

    return result


def _read_inifile_to_dict(config_path):
    """
    Read INI file from the provided path

    Returns: a dictionary representing the provided INI file content.

    An example return value:
    {
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
    """
    result = {}

    with contextlib.suppress(FileNotFoundError):
        with open(config_path) as f:
            parser = configparser.RawConfigParser()
            # prevent conversion of the opion name to lowercase
            parser.optionxform = lambda option: option
            parser.readfp(f)

            for section in parser.sections():
                section_config = dict(parser.items(section))
                if section_config:
                    result[section] = section_config

    return result


@define(slots=False)
class Dnf(Common):
    """
    Dnf
    """
    flatten = True
    dnf: dict

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read DNF configuration and defined variable files.

        Returns: dictionary with at most two keys 'dnf.conf' and 'vars'.
        'dnf.conf' value is a dictionary representing the DNF configuration
        file content.
        'vars' value is a dictionary which keys represent names of files from
        /etc/dnf/vars/ and values are strings representing the file content.

        An example return value:
        {
            "dnf.conf": {
                "main": {
                    "installonly_limit": "3"
                }
            },
            "vars": {
                "releasever": "8.4"
            }
        }
        """
        result = {}

        dnf_config = _read_inifile_to_dict(f"{tree}/etc/dnf/dnf.conf")
        if dnf_config:
            result["dnf.conf"] = dnf_config

        dnf_vars = {}
        for file in glob.glob(f"{tree}/etc/dnf/vars/*"):
            with open(file) as f:
                dnf_vars[os.path.basename(file)] = f.read().strip()
        if dnf_vars:
            result["vars"] = dnf_vars

        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        dnf = json_o.get("dnf")
        if dnf:
            return cls(dnf)
        return None
