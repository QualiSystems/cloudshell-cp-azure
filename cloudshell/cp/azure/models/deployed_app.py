from cloudshell.cp.core.request_actions import models
from cloudshell.shell.standards.core.resource_config_entities import ResourceAttrRO

from cloudshell.cp.azure import constants
from cloudshell.cp.azure.models.attributes import CustomTagsAttrRO


class BooleanResourceAttrRO(ResourceAttrRO):
    def __get__(self, instance, owner):
        """Get resource attribute.

        :param GenericResourceConfig instance:
        :rtype: str
        """
        if instance is None:
            return self

        attr = instance.attributes.get(self.get_key(instance), self.default)
        return attr.lower() == "true"


class BaseAzureVMDeployedApp(models.DeployedApp):
    resource_group_name = ResourceAttrRO("Resource Group Name", "DEPLOYMENT_PATH")

    allow_all_sandbox_traffic = BooleanResourceAttrRO(
        "Allow all Sandbox Traffic", "DEPLOYMENT_PATH"
    )
    extended_custom_tags = CustomTagsAttrRO("Custom Tags", "DEPLOYMENT_PATH")


class AzureVMFromMarketplaceDeployedApp(BaseAzureVMDeployedApp):
    DEPLOYMENT_PATH = constants.AZURE_VM_FROM_MARKETPLACE_DEPLOYMENT_PATH


class AzureVMFromCustomImageDeployedApp(BaseAzureVMDeployedApp):
    DEPLOYMENT_PATH = constants.AZURE_VM_FROM_CUSTOM_IMAGE_DEPLOYMENT_PATH


class AzureVMFromSharedGalleryImageDeployedApp(BaseAzureVMDeployedApp):
    DEPLOYMENT_PATH = constants.AZURE_VM_FROM_SHARED_GALLERY_IMAGE_DEPLOYMENT_PATH
