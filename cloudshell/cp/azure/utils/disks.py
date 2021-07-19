from dataclasses import dataclass

from azure.mgmt.compute.models import DiskStorageAccountTypes

from cloudshell.cp.azure.exceptions import (
    InvalidDiskTypeException,
    NoFreeDiskLunException,
)

DISK_TYPES_MAP = {
    "SSD": DiskStorageAccountTypes.premium_lrs,
    "HDD": DiskStorageAccountTypes.standard_lrs,
    # "STANDARD_SSD": DiskStorageAccountTypes.standard_ssd_lrs,  # noqa
    # "ULTRA_SSD": DiskStorageAccountTypes.ultra_ssd_lrs,  # noqa
}
MAX_DISK_LUN_NUMBER = 64


def get_azure_disk_type(disk_type: str):
    """Prepare Azure Disk type."""
    disk_type = disk_type.upper()

    if disk_type not in DISK_TYPES_MAP:
        raise InvalidDiskTypeException(
            f"Invalid Disk Type: {disk_type}. "
            f"Possible values are: {list(DISK_TYPES_MAP.keys())}"
        )

    return DISK_TYPES_MAP[disk_type]


def parse_data_disks_input(data_disks: str):
    """Parse Data Disks Input string."""
    disks = []

    for disk_data in (
        disk_data.strip() for disk_data in data_disks.split(";") if disk_data
    ):
        disk_name, disk_params = disk_data.split(":")

        try:
            disk_size, disk_type = disk_params.split(",")
        except ValueError:
            disk_size, disk_type = disk_params, None
        else:
            disk_type = get_azure_disk_type(disk_type)

        disk = DataDisk(name=disk_name, disk_size=disk_size, disk_type=disk_type)
        disks.append(disk)

    return disks


def get_disk_lun_generator(existing_disks=None):
    """Get generator for the next available disk LUN."""
    existing_disks_luns = [disk.lun for disk in existing_disks or []]

    for disk_lun in range(0, MAX_DISK_LUN_NUMBER + 1):
        if disk_lun not in existing_disks_luns:
            yield disk_lun

    raise NoFreeDiskLunException(
        "Unable to generate LUN for the disk. All LUNs numbers are in use"
    )


@dataclass
class DataDisk:
    DEFAULT_DISK_TYPE = DiskStorageAccountTypes.standard_lrs

    name: str
    disk_size: int
    disk_type: str = DEFAULT_DISK_TYPE
