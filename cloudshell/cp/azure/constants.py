SHELL_NAME = "Microsoft Azure Cloud Provider 2G"

AZURE_VM_FROM_MARKETPLACE_DEPLOYMENT_PATH = (
    f"{SHELL_NAME}.Azure VM From Marketplace 2nd Gen"
)
AZURE_VM_FROM_CUSTOM_IMAGE_DEPLOYMENT_PATH = (
    f"{SHELL_NAME}.Azure VM from Custom Image 2nd Gen"
)
AZURE_VM_FROM_SHARED_GALLERY_IMAGE_DEPLOYMENT_PATH = (
    f"{SHELL_NAME}.Azure VM from Gallery Image 2nd Gen"
)
AZURE_VM_LICENSES_MAP = {
    "No License": None,
    "Windows OS": "Windows_Client",
    "Windows Server OS": "Windows_Server",
    "Red Hat Enterprise Linux (RHEL)": "RHEL_BYOS",
    "SUSE Linux Enterprise Server (SLES)": "SLES_BYOS",
}

SUBNET_SERVICE_NAME_ATTRIBUTE = "Subnet Name"
