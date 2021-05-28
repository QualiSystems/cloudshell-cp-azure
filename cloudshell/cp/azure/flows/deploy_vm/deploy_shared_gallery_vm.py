from azure.mgmt.compute import models

from cloudshell.cp.azure.actions.vm_details import VMDetailsActions
from cloudshell.cp.azure.actions.vm_image import VMImageActions
from cloudshell.cp.azure.flows.deploy_vm.base_flow import BaseAzureDeployVMFlow


class AzureDeployGalleryImageVMFlow(BaseAzureDeployVMFlow):
    def _get_vm_image_os(self, deploy_app):
        """Get VM Image OS for shared gallery image.

        :param deploy_app:
        :return:
        """
        vm_image_actions = VMImageActions(
            azure_client=self._azure_client, logger=self._logger
        )

        return vm_image_actions.get_gallery_image_os(
            gallery_name=deploy_app.shared_image_gallery,
            gallery_image_name=deploy_app.image_definition,
            resource_group=deploy_app.shared_gallery_resource_group,
            subscription_id=deploy_app.shared_gallery_subscription_id,
        )

    def _prepare_storage_profile(self, deploy_app, os_disk):
        """Prepare Azure Storage Profile model for shared gallery image.

        :param deploy_app:
        :return:
        """
        vm_image_actions = VMImageActions(
            azure_client=self._azure_client, logger=self._logger
        )

        image_id = vm_image_actions.get_gallery_image_id(
            gallery_name=deploy_app.shared_image_gallery,
            gallery_image_name=deploy_app.image_definition,
            gallery_image_version=deploy_app.image_version,
            resource_group=deploy_app.shared_gallery_resource_group,
            subscription_id=deploy_app.shared_gallery_subscription_id,
        )

        return models.StorageProfile(
            os_disk=os_disk, image_reference=models.ImageReference(id=image_id)
        )

    def _prepare_vm_details_data(self, deployed_vm, resource_group_name):
        """Prepare CloudShell VM Details model.

        :param deployed_vm:
        :param resource_group_name:
        :return:
        """
        vm_details_actions = VMDetailsActions(
            azure_client=self._azure_client, logger=self._logger
        )
        return vm_details_actions.prepare_shared_gallery_vm_details(
            virtual_machine=deployed_vm, resource_group_name=resource_group_name
        )
