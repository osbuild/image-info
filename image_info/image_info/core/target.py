"""
Target definitions.
A Target represent a kind of "image" to analyse. That could be a tarball, a
compressed target, a Directory, an Ostree repo or commit and finally and Image.
Each one has a specific way of being loaded and are defined here.
"""
import mimetypes
from abc import ABC, abstractmethod
import glob
import os
import sys
import tempfile
import subprocess
import platform
import contextlib

from osbuild import loop

from image_info.report.inside_tree_element import find_all
from image_info.utils.utils import sanitize_name
from image_info.utils.loop import loop_open
from image_info.utils.mount import mount_at
from image_info.report.report import Report
from image_info.report.ostree import Type, Ostree
from image_info.report.inside_tree.boot_menu import Bootmenu
from image_info.report.inside_tree.boot_env import BootEnvironment

from image_info.report.image import ImageFormat, PartitionTable, Bootloader


class Target(ABC):
    """
    Abstract class that defines the Target framework. Each child class being
    able to handle a specific kind of images.
    """

    def __init__(self, target):
        self.target = target
        self.report = Report()

    @classmethod
    def match(cls, target):
        """
        returns True if the target can be handled by this class.
        """

    @abstractmethod
    def inspect(self):
        """
        explores the target and produces a JSON result
        """

    @classmethod
    def get(cls, target):
        """
        returns a specialized instance depending on the type of items archive we
        are dealing with.
        """
        if OSTreeTarget.match(target):
            return OSTreeTarget(target)
        if DirTarget.match(target):
            return DirTarget(target)
        if TarballTarget.match(target):
            return TarballTarget(target)
        if CompressedTarget.match(target):
            return CompressedTarget(target)
        return ImageTarget(target)

    @classmethod
    def from_json(cls, json_o):
        """
        Loads the proper target depending on the JSON content and returns a
        fully instantiated target.
        """
        if json_o.get("type") and "ostree" in json_o.get("type"):
            return OSTreeTarget.from_json(json_o)
        if json_o.get("image-format"):
            return ImageTarget.from_json(json_o)
        return DirTarget.from_json(json_o)

    def do_inside_tree_elements(self, tree, is_ostree=False):
        """
        Adds all the elements to the report
        """
        if os.path.exists(f"{tree}/etc/os-release"):
            inside_tree_elements = find_all()
            for ite in inside_tree_elements:
                ite_obj = ite.explore(tree, is_ostree)
                if ite_obj:
                    self.report.add_element(ite_obj)
        elif len(glob.glob(f"{tree}/vmlinuz-*")) > 0:
            self.report.add_element(BootEnvironment)
            self.report.add_element(Bootmenu)
        else:
            print("EFI partition", file=sys.stderr)

    def inside_tree_elements_from_json(self, json_o):
        """
        Loads all the ite elements from the input JSON
        """
        inside_tree_elements = find_all()
        for ite in inside_tree_elements:
            c_json_name = sanitize_name(ite.__name__)
            json_data = None
            if ite.flatten:
                json_data = json_o
            else:
                json_data = json_o.get(c_json_name)
            if json_data:
                with contextlib.suppress(KeyError):
                    ite_obj = ite.from_json(json_data)
                    if ite_obj:
                        self.report.add_element(ite_obj)


class TarballTarget(Target):
    """
    A tarball image can containe either a Tree or a raw image. The former must
    be handled as an DirTarget target and the later as an ImageTarget
    """

    @classmethod
    def match(cls, target):
        mtype, _ = mimetypes.guess_type(target)
        return mtype == "application/x-tar"

    def inspect(self):
        with tempfile.TemporaryDirectory(dir="/var/tmp") as tmpdir:
            tree = os.path.join(tmpdir, "root")
            os.makedirs(tree)
            command = [
                "tar",
                "--selinux",
                "--xattrs",
                "--acls",
                "-x",
                "--auto-compress",
                "-f", self.target,
                "-C", tree
            ]
            subprocess.run(command,
                           stdout=sys.stderr,
                           check=True)
            target = None
            if os.path.isfile(f"{tree}/disk.raw"):
                # gce image type contains virtual raw disk inside a tarball
                target = Target.get(f"{tree}/disk.raw")
                target.inspect()
            else:
                target = Target.get(tree)
                target.inspect()
            self.report = target.report


class CompressedTarget(Target):
    """
    A compressed target contains an image that needs first to be decompressed.
    """

    def __init__(self, target):
        super().__init__(target)
        self.target = target
        _, encoding = mimetypes.guess_type(self.target)
        if encoding == "xz":
            self.command = ["unxz", "--force"]
        elif encoding == "gzip":
            self.command = ["gunzip", "--force"]
        elif encoding == "bzip2":
            self.command = ["bunzip2", "--force"]
        else:
            raise ValueError(f"Unsupported compression: {encoding}")

    @classmethod
    def match(cls, target):
        _, encoding = mimetypes.guess_type(target)
        return encoding in ["xz", "gzip", "bzip2"]

    def inspect(self):
        with tempfile.TemporaryDirectory(dir="/var/tmp") as tmpdir:
            subprocess.run(
                ["cp", "--reflink=auto", "-a",
                 self.target,
                 tmpdir],
                check=True)

            files = os.listdir(tmpdir)
            archive = os.path.join(tmpdir, files[0])
            subprocess.run(self.command + [archive], check=True)

            files = os.listdir(tmpdir)
            assert len(files) == 1
            target = ImageTarget(os.path.join(tmpdir, files[0]))
            target.inspect()
            self.report = target.report


class DirTarget(Target):
    """
    Handles a directory. A directory can be either an ostree commit, and ostree
    repo or a simple directory.
    """

    @classmethod
    def match(cls, target):
        return os.path.isdir(target)

    def inspect(self):
        with tempfile.TemporaryDirectory(dir="/var/tmp") as tmpdir:
            tree_ro = os.path.join(tmpdir, "root_ro")
            os.makedirs(tree_ro)
            # Make sure that the tools which analyse the directory in-place
            # can not modify its content (e.g. create additional files).
            # mount_at() always mounts the source as read-only!
            with mount_at(self.target, tree_ro, ["bind"]) as _mountpoint:
                self.do_inside_tree_elements(tree_ro)

    @classmethod
    def from_json(cls, json_o):
        dtt = cls(None)
        dtt.inside_tree_elements_from_json(json_o)
        return dtt


class OSTreeTarget(Target):
    """
    Handles an OSTree folder.
    """

    @classmethod
    def match(cls, target):
        return (os.path.isdir(os.path.join(target, 'refs')) or
                os.path.exists(os.path.join(target, 'compose.json')))

    def inspect(self):
        self.report.add_element(Type.from_device(self.target))
        target = os.path.join(self.target, "repo")
        ostree = Ostree.from_device(target)
        self.report.add_element(ostree)

        with ostree.mount(target) as tree:
            with tempfile.TemporaryDirectory(dir="/var/tmp") as tmpdir:
                tree_ro = os.path.join(tmpdir, "root_ro")
                os.makedirs(tree_ro)
                # Make sure that the tools which analyse the directory in-place
                # can not modify its content (e.g. create additional files).
                # mount_at() always mounts the source as read-only!
                with mount_at(tree, tree_ro, ["bind"]) as _:
                    os.makedirs(f"{tree}/etc", exist_ok=True)
                    with mount_at(
                            f"{tree}/usr/etc", f"{tree}/etc", extra=["--bind"]):
                        self.do_inside_tree_elements(tree_ro, is_ostree=True)

    @classmethod
    def from_json(cls, json_o):
        ott = cls(None)
        ott.report.add_element(Type.from_json(json_o))
        ott.report.add_element(Ostree.from_json(json_o["ostree"]))
        ott.inside_tree_elements_from_json(json_o)
        return ott


class ImageTarget(Target):
    """
    Handles an image.
    """

    def inspect(self):
        self.report.add_element(ImageFormat.from_device(self.target))
        with FileSystemMounter(self.target).mount() as device, tree:
            self.report.add_element(Bootloader.from_device(device))
            self.report.add_element(PartitionTable.from_device(device))
            self.do_inside_tree_elements(tree)

    @classmethod
    def from_json(cls, json_o):
        imt = cls(None)
        imt.report.add_element(ImageFormat.from_json(json_o))
        imt.report.add_element(Bootloader.from_json(json_o))
        part_table = PartitionTable.from_json(json_o)
        imt.report.add_element(part_table)
        # Due to the current format of the image_info,
        # sometimes these elements have different values
        # depending on the context and this could be `None`.
        # For now we need to check for this, but we could
        # possibly refactor this in the future at the cost
        # of breaking compatibility.
        if part_table.partition_table_id:
            imt.inside_tree_elements_from_json(json_o)
        return imt
