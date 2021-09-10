from dataclasses import dataclass

from azure.mgmt.compute.models import StorageAccountTypes

from cloudshell.cp.azure.exceptions import (
    InvalidDiskTypeException,
    NoFreeDiskLunException,
)

# CloudShell disks types format
STANDARD_HDD_LRS = "Standard HDD"
STANDARD_SSD_LRS = "Standard SSD"
PREMIUM_SSD_LRS = "Premium SSD"
ULTRA_SSD_LRS = "Ultra SSD"
STANDARD_SSD_ZRS = "Standard SSD (zone-redundant storage)"
PREMIUM_SSD_ZRS = "Premium SSD (zone-redundant storage)"

AZURE_TO_CS_DISKS_TYPES_MAP = {
    StorageAccountTypes.standard_lrs: STANDARD_HDD_LRS,
    StorageAccountTypes.standard_ssd_lrs: STANDARD_SSD_LRS,
    StorageAccountTypes.premium_lrs: PREMIUM_SSD_LRS,
    StorageAccountTypes.ultra_ssd_lrs: ULTRA_SSD_LRS,
    "StandardSSD_ZRS": STANDARD_SSD_ZRS,  # todo: update compute client
    "Premium_ZRS": PREMIUM_SSD_ZRS,  # todo: update compute client
}

CS_TO_AZURE_DISKS_TYPES_MAP = {
    val.upper(): key for key, val in AZURE_TO_CS_DISKS_TYPES_MAP.items()
}

DEPRECATED_CS_TO_AZURE_DISKS_TYPES_MAP = {
    "HDD": StorageAccountTypes.standard_lrs,
    "SSD": StorageAccountTypes.premium_lrs,
}

MAX_DISK_LUN_NUMBER = 64
DATA_DISK_NAME_TPL = "{vm_name}_{disk_name}"


def convert_cs_to_azure_os_disk_type(disk_type: str):
    """Convert CloudShell OS disk type to the Azure format."""
    os_disk_types_map = CS_TO_AZURE_DISKS_TYPES_MAP.copy()
    del os_disk_types_map[
        ULTRA_SSD_LRS.upper()
    ]  # Ultra SSD LRS cannot be used with the OS Disk

    return _get_azure_disk_type(disk_type=disk_type, disk_types_map=os_disk_types_map)


def convert_cs_to_azure_data_disk_type(disk_type: str):
    """Convert CloudShell data disk type to the Azure format."""
    return _get_azure_disk_type(
        disk_type=disk_type, disk_types_map=CS_TO_AZURE_DISKS_TYPES_MAP
    )


def convert_azure_to_cs_disk_type(azure_disk_type: str):
    """Convert Azure disk type to CloudShell format."""
    return AZURE_TO_CS_DISKS_TYPES_MAP.get(azure_disk_type, azure_disk_type)


def _get_azure_disk_type(disk_type: str, disk_types_map: dict):
    """Prepare Azure Disk type."""
    all_disk_types_map = {**disk_types_map, **DEPRECATED_CS_TO_AZURE_DISKS_TYPES_MAP}
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
            disk_type = convert_cs_to_azure_data_disk_type(disk_type)

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


def prepare_full_data_disk_name(disk_name, vm_name):
    """Prepare full Data disk name with VM name prefix."""
    return DATA_DISK_NAME_TPL.format(disk_name=disk_name, vm_name=vm_name)


def get_display_data_disk_name(full_disk_name, vm_name):
    """Get Data disk name without VM name prefix."""
    disk_name_prefix = DATA_DISK_NAME_TPL.format(vm_name=vm_name, disk_name="")
    return full_disk_name.replace(disk_name_prefix, "")


@dataclass
class DataDisk:
    DEFAULT_DISK_TYPE = StorageAccountTypes.standard_lrs

    name: str
    disk_size: int
    disk_type: str = DEFAULT_DISK_TYPE
