"""
Holds the necessary classes and function to load and mount a file system.
"""
import os
import contextlib
import subprocess
from collections import OrderedDict
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Iterator
try:
    from attr import define, field
except ImportError:
    from attr import s as define
    from attr import ib as field

from image_info.utils.mount import mount, mount_at
from image_info.report.report import ReportElement
from image_info.utils.loop import loop_open
from image_info.utils.utils import parse_environment_vars
from image_info.utils.lvm import ensure_device_file, volume_group_for_device


#pylint: disable=too-few-public-methods


@define
class FstabEntry:
    """
    Contain an extracted line of an fstab. Can be used to mount the file system.
    """
    uuid: str = field()
    mountpoint: str = field()
    fstype: str = field()
    options: str = field()

    @classmethod
    def read_fstab(cls, tree):
        """
        Read the content of /etc/fstab in the tree.

        Returns a Fstab object contaning an entry for each all uncommented lines
        read from the configuration file.
        """
        fstabs = []
        with contextlib.suppress(FileNotFoundError):
            #pylint: disable=unspecified-encoding
            with open(f"{tree}/etc/fstab") as file:
                result = sorted(
                    [line.split() for line in file
                        if line.strip() and not line.startswith("#")])
                for fstab_entry in result:
                    fstabs.append(
                        FstabEntry(
                            fstab_entry[0].split("=")[1].upper(),
                            fstab_entry[1],
                            fstab_entry[2],
                            fstab_entry[3].split(",")))
        if fstabs:
            # sort the fstab entries by the mountpoint
            fstabs.sort(key=lambda x: x.mountpoint)
            return fstabs
        return None


@define
class FileSystem:
    """
    A FileSystem can:
    - be mounted to search for an fstab
    - be mounted to a fstab location (provided the fstab_entry to refer to)
    """
    uuid: str = field()
    device: str = field()
    mntops: list = field()

    def fstab(self) -> Optional[List[FstabEntry]]:
        """
        Returns the fstab from the FileSystem if it exists.
        """
        with mount(self.device, self.mntops) as tree:
            if os.path.exists(f"{tree}/etc/fstab"):
                return FstabEntry.read_fstab(tree)
        return None

    def mount_root(self, options, context, _fstype) -> str:
        """
        mount the FileSystem as the root. """
        options = options if options else []
        mntops = options + self.mntops if self.mntops else options
        return context.enter_context(mount(self.device, mntops))

    def mount_at(self, context, options, mountpoint, fstype):
        """
        mount the FileSystem at a specific mountpoint
        """
        options = options if options else []
        mntops = options + self.mntops if self.mntops else options
        context.enter_context(
            mount_at(
                self.device,
                mountpoint,
                options=mntops,
                extra=["-t", fstype]))


#pylint: disable=too-few-public-methods
class FileSystemFactory(ABC):
    """
    A contract to implement in order to be considered a FileSystem generator
    """

    @abstractmethod
    def fsystems(self) -> List[FileSystem]:
        """
        Returns a list of FileSystem objects corresponding to the volume or
        subvolumes of a partition
        """


@define(slots=False)
class GenericPartition():
    uuid: str = field(init=False, default=None)
    fstype: str = field(init=False, default=None)

    def read_generics(self, device):
        res = subprocess.run(["blkid", "-c", "/dev/null", "--output", "export",
                              device],
                             check=False, encoding="utf-8",
                             stdout=subprocess.PIPE)
        if res.returncode == 0:
            blkid = parse_environment_vars(res.stdout)
            self.uuid = blkid.get("UUID")
            self.fstype = blkid.get("TYPE")

    def copy_from(self, other):
        """
        Copy the fields from another GenericPartition
        """
        self.uuid = other.uuid
        self.fstype = other.fstype


@ define(slots=False)
class ImagePartition(GenericPartition, FileSystemFactory):
    partuuid: str = field()
    start: int = field()
    size: int = field()
    type: str = field()

    def explore(self, device, loctl, context):
        """
        Explore the partition:
            - mount the device at the spot the partition is on
            - read the information found there
            - if the partition is an lvm one:
                - transform the partition as a LvmPartition
        """
        # open the partition and read info
        dev = self.open(loctl, device, context)
        # update the partition information from the mounted device
        self.read_generics(dev)
        # detect if the partition is an lvm partition, transform it if it is
        if self.is_lvm():
            return self.to_lvm_partition(dev, context)
        # pylint: disable=attribute-defined-outside-init
        self.device = dev
        return self

    def open(self, loctl, device, context):
        """
        Opens the partition and returns a device to access it
        """
        return context.enter_context(
            loop_open(
                loctl,
                device,
                offset=self.start,
                size=self.size))

    def is_lvm(self) -> bool:
        """
        Returns true if the partition is an LVM partition
        """
        return self.type.upper() in ["E6D6D379-F507-44C2-A23C-238F2A3DF928",
                                     "8E"]

    def to_lvm_partition(self, dev, context_manager):
        """
        Transform a simple image partition into an lvm one
        """
        return context_manager.enter_context(LvmPartition.discover_lvm(dev,
                                                                       self))

    def fsystems(self):
        """
        Return a list of FileSystem objects, one for each partition contained in
        this partition.
        """
        if self.uuid and self.fstype:
            return [FileSystem(self.uuid.upper(), self.device, None)]
        return []


@ define(slots=False)
class LvmVolume(GenericPartition):
    """
    Inheriting from GenericPartition a LvmVolume just keeps track of the
    information gathered by reading the device. The class brings the ability to
    obtain a FileSystem object out of the partition with the fs method in order
    to be mounted with special care.
    """

    def __init__(self):
        self.device = None

    def file_system(self):
        """
        return a FileSystem object having special mounting options
        """
        if self.fstype:
            mntopts = []
            # we cannot recover since the underlying loopback
            # device is mounted read-only but since we are using
            # the it through the device mapper the fact might
            # not be communicated and the kernel attempt a to a
            # recovery of the filesystem, which will lead to a
            # kernel panic
            if self.fstype in ("ext4", "ext3", "xfs"):
                mntopts = ["norecovery"]
            # the device attribute is set outside of the attrs context in order
            # to keep the value out of the generated dict by asdict()
            # pylint: disable=no-member
            return FileSystem(self.uuid.upper(), self.device, mntopts)
        return None


@ define(slots=False)
class LvmPartition(ImagePartition):
    """
    An lvm partition contains subvolumes that are stored as a list.
    """
    lvm__vg: str = field()
    lvm__volumes: Dict[str, LvmVolume] = field()

    @ classmethod
    @ contextlib.contextmanager
    def discover_lvm(cls, dev, partition) -> Iterator:
        """
        discover all the volumes under the current partition
        """
        # find the volume group name for the device file
        vg_name = volume_group_for_device(dev)

        # activate it
        res = subprocess.run(["vgchange", "-ay", vg_name],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE,
                             check=False)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.strip())

        try:
            # Find all logical volumes in the volume group
            cmd = [
                "lvdisplay", "-C", "--noheadings",
                "-o", "lv_name,path,lv_kernel_major,lv_kernel_minor",
                "--separator", ";",
                vg_name
            ]

            res2 = subprocess.run(cmd, check=False, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, encoding="UTF-8")

            if res2.returncode != 0:
                raise RuntimeError(res2.stderr.strip())

            data = res2.stdout.strip()
            parsed = list(map(lambda l: l.split(";"), data.split("\n")))
            volumes = OrderedDict()

            for vol in parsed:
                vol = list(map(lambda v: v.strip(), vol))
                assert len(vol) == 4
                name, voldev, major, minor = vol
                ensure_device_file(voldev, int(major), int(minor))

                volumes[name] = LvmVolume()
                volumes[name].read_generics(voldev)
                if name.startswith("root"):
                    volumes.move_to_end(name, last=False)
                # setting this attribute outside of attrs makes the library
                # blind to it, so it will not show in the asdict() result, but
                # we still can use it
                # pylint: disable=attribute-defined-outside-init
                volumes[name].device = voldev
            lvm_partition = cls(
                partition.partuuid,
                partition.start,
                partition.size,
                partition.type,
                vg_name,
                volumes)
            lvm_partition.copy_from(partition)
            yield lvm_partition

        finally:
            res = subprocess.run(["vgchange", "-an", vg_name],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE,
                                 check=False)
            if res.returncode != 0:
                raise RuntimeError(res.stderr.strip())

    def fsystems(self):
        fsystems = []
        for _, volume in self.lvm__volumes.items():
            file_system = volume.file_system()
            if file_system:
                fsystems.append(file_system)
        return fsystems


class Mounter:

    def __init__(self, target):
        self.target = target

    def mount(self):
        pass


class FileSystemMounter(Mounter):
    """
    A FileSystem object can mount the entire FS if it contains a FStab.
    """

    @ contextlib.contextmanager
    def open_target(self, ctl, image_format):
        """
        Opens the image in a loopback device. Apply qemu convertion if necessary
        """
        with tempfile.TemporaryDirectory(dir="/var/tmp") as tmp:
            if image_format.image_format["type"] != "raw":
                target = os.path.join(tmp, "image.raw")
                # a bug exists in qemu that causes the conversion to raw to fail
                # on aarch64 systems with a lot of cpus. A workaround is to use
                # a single coroutine to do the conversion. It doesn't slow down
                # the conversion by much, but it hangs about half the time
                # without the limit set. 😢
                # bug: https://bugs.launchpad.net/qemu/+bug/1805256
                if platform.machine() == 'aarch64':
                    subprocess.run(
                        ["qemu-img", "convert", "-m", "1", "-O", "raw",
                            self.target,
                            target], check=True
                    )
                else:
                    subprocess.run(
                        ["qemu-img", "convert", "-O", "raw", self.target,
                            target], check=True
                    )
            else:
                target = self.target

            size = os.stat(target).st_size

            with loop_open(ctl, target, offset=0, size=size) as dev:
                yield dev

    def get(self, uuid):
        """
        return a FileSystem by its uuid
        """
        for fsystem in self.fss:
            if fsystem.uuid == uuid:
                return fsystem
        return None

    @contextlib.contextmanager
    def mount_partitions(self, device, loctl, context):
        try:
            sfdisk = subprocess_check_output(
                ["sfdisk", "--json", device], json.loads)
        except subprocess.CalledProcessError:
            # This handles a case, when the device does contain a filesystem,
            # but there is no partition table.
            part1 = GenericPartition()
            part1.read_generics(self.device)
            with mount(device) as tree:
                yield device, tree

        ptable = sfdisk["partitiontable"]
        assert ptable["unit"] == "sectors"
        is_dos = ptable["label"] == "dos"
        ssize = ptable.get("sectorsize", 512)

        partitions = []
        for i, partition in enumerate(ptable["partitions"]):
            partuuid = partition.get("uuid")
            if not partuuid and is_dos:
                # For dos/mbr partition layouts the partition uuid
                # is generated. Normally this would be done by
                # udev+blkid, when the partition table is scanned.
                # 'sfdisk' prefixes the partition id with '0x' but
                # 'blkid' does not; remove it to mimic 'blkid'
                table_id = ptable['id'][2:]
                partuuid = f"{table_id:.33s}-{i+1:02x}"

            partitions.append(ImagePartition(
                partuuid,
                partition["start"] * ssize,
                partition["size"] * ssize,
                partition["type"]).explore(device, loctl, context))

        partitions.sort(key=lambda x: x.partuuid)
        yield device, self.__mount_all(partitions, context)

    @contextlib.contextmanager
    def mount(self):
        loctl = loop.LoopControl()
        with contextlib.ExitStack() as context:
            with self.open_target(loctl, image_format) as device:
                self.mount_partitions(device, loctl, context)

    def __mount_all(self):
        """
        Find the FileSystem holding the FStab, extract it and mount all the
        FileSystems according to it.
        """
        self.fss: List[FileSystem] = []
        # generate the fs mount values for each partition and volumes
        for partition in self.partitions:
            self.fss.extend(partition.fsystems())

        for fsystem in self.fss:
            fstab = fsystem.fstab()
            if fstab:
                break

        root_tree = None
        for fstab_entry in fstab:
            fsystem = self.get(fstab_entry.uuid)
            if root_tree is None:
                # the first mount point should be root
                if fstab_entry.mountpoint != "/":
                    raise RuntimeError(
                        "The first mountpoint in sorted fstab entries is not '/'")
                root_tree = fsystem.mount_root(fstab_entry.options,
                                               context,
                                               fstab_entry.fstype)
            else:
                fsystem.mount_at(context,
                                 fstab_entry.options,
                                 f"{root_tree}{fstab_entry.mountpoint}",
                                 fstab_entry.fstype)

        if not root_tree:
            raise RuntimeError("The root filesystem tree is not mounted")
        return root_tree
