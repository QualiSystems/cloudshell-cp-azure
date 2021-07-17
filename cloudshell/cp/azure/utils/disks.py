from dataclasses import dataclass

from azure.mgmt.compute.models import StorageAccountTypes

from cloudshell.cp.azure.exceptions import (
    InvalidDiskTypeException,
    NoFreeDiskLunException,
)

STANDARD_HDD_LRS = "STANDARD HDD"
STANDARD_SSD_LRS = "STANDARD SSD"
PREMIUM_SSD_LRS = "PREMIUM SSD"
ULTRA_SSD_LRS = "ULTRA SSD"
STANDARD_SSD_ZRS = "STANDARD SSD (ZONE-REDUNDANT STORAGE)"
PREMIUM_SSD_ZRS = "PREMIUM SSD (ZONE-REDUNDANT STORAGE)"

DISK_TYPES_MAP = {
    STANDARD_HDD_LRS: StorageAccountTypes.standard_lrs,
    STANDARD_SSD_LRS: StorageAccountTypes.standard_ssd_lrs,
    PREMIUM_SSD_LRS: StorageAccountTypes.premium_lrs,
    ULTRA_SSD_LRS: StorageAccountTypes.ultra_ssd_lrs,
    STANDARD_SSD_ZRS: "StandardSSD_ZRS",  # todo: update compute client
    PREMIUM_SSD_ZRS: "Premium_ZRS",  # todo: update compute client
}

DEPRECATED_DISK_TYPES_MAP = {
    "HDD": StorageAccountTypes.standard_lrs,
    "SSD": StorageAccountTypes.premium_lrs,
}

MAX_DISK_LUN_NUMBER = 64


def get_azure_os_disk_type(disk_type: str):
    """Prepare Azure OS Disk type."""
    os_disk_types_map = DISK_TYPES_MAP.copy()
    del os_disk_types_map[
        ULTRA_SSD_LRS
    ]  # Ultra SSD LRS cannot be used with the OS Disk

    return _get_azure_disk_type(disk_type=disk_type, disk_types_map=os_disk_types_map)


def get_azure_data_disk_type(disk_type: str):
    """Prepare Azure Data Disk type."""
    return _get_azure_disk_type(disk_type=disk_type, disk_types_map=DISK_TYPES_MAP)


def _get_azure_disk_type(disk_type: str, disk_types_map: dict):
    """Prepare Azure Disk type."""
    all_disk_types_map = {**disk_types_map, **DEPRECATED_DISK_TYPES_MAP}
    disk_type = disk_type.upper()

    if disk_type not in all_disk_types_map:
        raise InvalidDiskTypeException(
            f"Invalid Disk Type: '{disk_type}'. "
            f"Possible values are: {list(disk_types_map.keys())}"
        )

    return all_disk_types_map[disk_type]


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
            disk_type = get_azure_data_disk_type(disk_type)

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


def is_ultra_disk_in_list(data_disks):
    """Check if there is an Ultra SDD Disk."""
    for disk in data_disks:
        if disk.sku.name == StorageAccountTypes.ultra_ssd_lrs:
            return True

    return False


@dataclass
class DataDisk:
    DEFAULT_DISK_TYPE = StorageAccountTypes.standard_lrs

    name: str
    disk_size: int
    disk_type: str = DEFAULT_DISK_TYPE
