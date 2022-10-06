"""
Configuration files
"""
from typing import Dict
from attr import define
from image_info.report.common import Common
from image_info.common.sshd_config import SSHConfig
from image_info.utils.files import _read_glob_paths_with_parser


@define(slots=False)
class SSHDConfig(Common):
    """
    SSHConfig
    """
    flatten = True
    sshd_config: Dict

    @classmethod
    def explore(cls, tree, _is_ostree=False):
        """
        Read all SSHd configuration files from a predefined list of paths and
        parse them.

        The searched paths are:
        - "/etc/ssh/sshd_config"
        - "/etc/ssh/sshd_config.d/*.conf"

        Returns: dictionary as returned by '_read_glob_paths_with_parser()' with
        configuration representation as returned by 'read_ssh_config()'.

        An example return value:
        {
            "/etc/ssh": {
                "sshd_config": [
                    "HostKey /etc/ssh/ssh_host_rsa_key",
                    "HostKey /etc/ssh/ssh_host_ecdsa_key",
                    "HostKey /etc/ssh/ssh_host_ed25519_key",
                    "SyslogFacility AUTHPRIV",
                    "PermitRootLogin no",
                    "AuthorizedKeysFile\t.ssh/authorized_keys",
                    "PasswordAuthentication no",
                    "ChallengeResponseAuthentication no",
                    "GSSAPIAuthentication yes",
                    "GSSAPICleanupCredentials no",
                    "UsePAM yes",
                    "X11Forwarding yes",
                    "PrintMotd no",
                    "AcceptEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES",
                    "AcceptEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT",
                    "AcceptEnv LC_IDENTIFICATION LC_ALL LANGUAGE",
                    "AcceptEnv XMODIFIERS",
                    "Subsystem\tsftp\t/usr/libexec/openssh/sftp-server",
                    "ClientAliveInterval 420"
                ]
            }
        }
        """
        checked_globs = [
            "/etc/ssh/sshd_config",
            "/etc/ssh/sshd_config.d/*.conf"
        ]

        result = _read_glob_paths_with_parser(
            tree, checked_globs, SSHConfig.read_ssh_config)
        if result:
            return cls(result)
        return None

    @classmethod
    def from_json(cls, json_o):
        ssh = json_o.get("sshd_config")
        if ssh:
            return cls(ssh)
        return None
