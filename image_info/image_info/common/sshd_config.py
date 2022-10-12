"""
Configuration files
"""
from attr import define
from image_info.report.common import Common
from image_info.utils.files import _read_glob_paths_with_parser


@define(slots=False)
class SSHConfig(Common):
    """
    SSHConfig
    """
    flatten = True
    ssh_config: dict

    @staticmethod
    def read_ssh_config(config_path):
        """
        Read the content of provided SSH(d) configuration file.

        Returns: list of uncommented and non-empty lines read from the configuation
        file.

        An example return value:
        [
            "Match final all",
            "Include /etc/crypto-policies/back-ends/openssh.config",
            "GSSAPIAuthentication yes",
            "ForwardX11Trusted yes",
            "SendEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES",
            "SendEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT",
            "SendEnv LC_IDENTIFICATION LC_ALL LANGUAGE",
            "SendEnv XMODIFIERS"
        ]
        """
        config_lines = []

        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line[0] == "#":
                    continue
                config_lines.append(line)

        return config_lines

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all SSH configuration files from a predefined list of paths and
        parse them.

        The searched paths are:
        - "/etc/ssh/ssh_config"
        - "/etc/ssh/ssh_config.d/*.conf"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by 'read_ssh_config()'.

        An example return value:
        {
            "/etc/ssh": {
                "ssh_config": [
                    "Include /etc/ssh/ssh_config.d/*.conf"
                ]
            },
            "/etc/ssh/ssh_config.d": {
                "05-redhat.conf": [
                    "Match final all",
                    "Include /etc/crypto-policies/back-ends/openssh.config",
                    "GSSAPIAuthentication yes",
                    "ForwardX11Trusted yes",
                    "SendEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES",
                    "SendEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT",
                    "SendEnv LC_IDENTIFICATION LC_ALL LANGUAGE",
                    "SendEnv XMODIFIERS"
                ]
            }
        }
        """
        checked_globs = [
            "/etc/ssh/ssh_config",
            "/etc/ssh/ssh_config.d/*.conf"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, SSHConfig.read_ssh_config)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        ssh = json_o.get("ssh_config")
        if ssh:
            return cls(ssh)
        return None
