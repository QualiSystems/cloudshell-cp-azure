from cloudshell.cp.core.request_actions import models
from cloudshell.shell.standards.core.resource_config_entities import (
    ResourceAttrRO,
    ResourceBoolAttrRO,
)

from cloudshell.cp.azure import constants
from cloudshell.cp.azure.models.attributes import (
    CustomTagsAttrRO,
    DataDisksAttrRO,
    InboundPortsAttrRO,
    IntegerAttrRO,
    LicenseTypeAttrRO,
)


class BaseAzureVMDeployApp(models.DeployApp):
    @property
    def app_name(self):
        return self.actionParams.appName.lower().replace(" ", "-")

    vm_size = ResourceAttrRO("VM Size", "DEPLOYMENT_PATH")

    disk_type = ResourceAttrRO("Disk Type", "DEPLOYMENT_PATH")

    disk_size = ResourceAttrRO("Disk Size", "DEPLOYMENT_PATH")

    data_disks = DataDisksAttrRO("Data Disks", "DEPLOYMENT_PATH")

    license_type = LicenseTypeAttrRO("License Type", "DEPLOYMENT_PATH")

    enable_boot_diagnostics = ResourceBoolAttrRO(
        "Enable Boot Diagnostics", "DEPLOYMENT_PATH"
    )

    boot_diagnostics_storage_account = ResourceAttrRO(
        "Boot Diagnostics Storage Account", "DEPLOYMENT_PATH"
    )

    resource_group_name = ResourceAttrRO("Resource Group Name", "DEPLOYMENT_PATH")

    add_public_ip = ResourceBoolAttrRO("Add Public IP", "DEPLOYMENT_PATH")

    wait_for_ip = ResourceBoolAttrRO("Wait for IP", "DEPLOYMENT_PATH")

    extension_script_file = ResourceAttrRO("Extension Script file", "DEPLOYMENT_PATH")

    extension_script_configurations = ResourceAttrRO(
        "Extension Script Configurations", "DEPLOYMENT_PATH"
    )

    extension_script_timeout = IntegerAttrRO(
        "Extension Script Timeout", "DEPLOYMENT_PATH"
    )

    public_ip_type = ResourceAttrRO("Public IP Type", "DEPLOYMENT_PATH")

    inbound_ports = InboundPortsAttrRO("Inbound Ports", "DEPLOYMENT_PATH")

    extended_custom_tags = CustomTagsAttrRO("Custom Tags", "DEPLOYMENT_PATH")

    enable_ip_forwarding = ResourceBoolAttrRO("Enable IP Forwarding", "DEPLOYMENT_PATH")

    allow_all_sandbox_traffic = ResourceBoolAttrRO(
        "Allow all Sandbox Traffic", "DEPLOYMENT_PATH"
    )


class AzureVMFromMarketplaceDeployApp(BaseAzureVMDeployApp):
    DEPLOYMENT_PATH = constants.AZURE_VM_FROM_MARKETPLACE_DEPLOYMENT_PATH

    image_publisher = ResourceAttrRO("Image Publisher", "DEPLOYMENT_PATH")

    image_offer = ResourceAttrRO("Image Offer", "DEPLOYMENT_PATH")

    image_sku = ResourceAttrRO("Image SKU", "DEPLOYMENT_PATH")

    image_version = ResourceAttrRO("Image Version", "DEPLOYMENT_PATH")


class AzureVMFromCustomImageDeployApp(BaseAzureVMDeployApp):
    DEPLOYMENT_PATH = constants.AZURE_VM_FROM_CUSTOM_IMAGE_DEPLOYMENT_PATH

    azure_image = ResourceAttrRO("Azure Image", "DEPLOYMENT_PATH")

    azure_resource_group = ResourceAttrRO("Azure Resource Group", "DEPLOYMENT_PATH")


class AzureVMFromSharedGalleryImageDeployApp(BaseAzureVMDeployApp):
    DEPLOYMENT_PATH = constants.AZURE_VM_FROM_SHARED_GALLERY_IMAGE_DEPLOYMENT_PATH

    shared_image_gallery = ResourceAttrRO("Shared Image Gallery", "DEPLOYMENT_PATH")
    image_definition = ResourceAttrRO("Image Definition", "DEPLOYMENT_PATH")
    image_version = ResourceAttrRO("Image Version", "DEPLOYMENT_PATH")

    shared_gallery_resource_group = ResourceAttrRO(
        "Shared Gallery Resource Group", "DEPLOYMENT_PATH"
    )
    shared_gallery_subscription_id = ResourceAttrRO(
        "Shared Gallery Subscription ID", "DEPLOYMENT_PATH"
    )
