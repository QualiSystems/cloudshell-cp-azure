import requests
from azure.mgmt.compute.models import OperatingSystemTypes
from msrestazure.azure_exceptions import CloudError
from requests.utils import is_valid_cidr

from cloudshell.cp.azure.actions.network import NetworkActions
from cloudshell.cp.azure.utils.tags import get_default_tags_count


class ValidationActions(NetworkActions):
    MAX_VM_DISK_SIZE_GB = 1023
    MAX_TAGS_NUMBER = 15

    def register_azure_providers(self):
        """Register Azure Providers.

        :return:
        """
        self._logger.info("Registering subscription with Azure providers...")
        for provider in (
            "Microsoft.Authorization",
            "Microsoft.Storage",
            "Microsoft.Network",
            "Microsoft.Compute",
        ):

            self._logger.info(
                f"Registering subscription with a {provider} resource provider"
            )
            self._azure_client.register_provider(provider)

    def validate_azure_region(self, region):
        """Validate Azure Region.

        :param str region:
        :return:
        """
        self._logger.info("Validating Azure region...")

        if not region:
            raise Exception("Region attribute can not be empty")

        available_regions = [
            available_region.name
            for available_region in self._azure_client.get_available_regions()
        ]
        self._logger.debug(f"Available Azure regions: {available_regions}")

        if region not in available_regions:
            raise Exception(f'Region "{region}" is not a valid Azure Geo-location')

    def validate_azure_mgmt_resource_group(self, mgmt_resource_group_name, region):
        """Validate Management Resource Group.

        :param str mgmt_resource_group_name:
        :param str region:
        :return:
        """
        self._logger.info(
            f"Validating MGMT resource group {mgmt_resource_group_name}..."
        )

        try:
            resource_group = self._azure_client.get_resource_group(
                mgmt_resource_group_name
            )
        except CloudError:
            error_msg = (
                f"Failed to find management resource group '{mgmt_resource_group_name}'"
            )
            self._logger.exception(error_msg)
            raise Exception(error_msg)

        if region != resource_group.location:
            raise Exception(
                f"Management group '{mgmt_resource_group_name}' "
                f"is not under the '{region}' region"
            )

    def validate_azure_sandbox_network(self, mgmt_resource_group_name):
        """Validate Azure Sandbox vNET.

        :param str mgmt_resource_group_name:
        :return:
        """
        self._logger.info(
            "Verifying that sandbox vNet exists under the MGMT resource group..."
        )
        self.get_sandbox_virtual_network(resource_group_name=mgmt_resource_group_name)

    def validate_azure_vm_size(self, vm_size, region):
        """Validate 'VM Size' attribute.

        :param str vm_size:
        :param str region:
        :return:
        """
        self._logger.info(f"Validating VM size {vm_size}")
        if vm_size:
            available_vm_sizes = [
                vm_size.name
                for vm_size in self._azure_client.get_virtual_machine_sizes_by_region(
                    region
                )
            ]

            self._logger.debug(f"Available VM sizes: {available_vm_sizes}")

            if vm_size not in available_vm_sizes:
                raise Exception(f"VM Size {vm_size} is not valid")

    def validate_custom_tags(self, custom_tags):
        """Validate resource 'Custom tags' attribute".

        :param dict custom_tags:
        :return:
        """
        self._logger.info("Validating 'Custom Tags' attribute")
        allowed_tags_number = self.MAX_TAGS_NUMBER - get_default_tags_count()

        if len(custom_tags) > allowed_tags_number:
            raise Exception(
                f"The number of Azure custom tags must be no more than "
                f"{allowed_tags_number}. Present number of custom tags: "
                f"{len(custom_tags)}"
            )

    def validate_tags(self, tags):
        """Validate resource and deployment path 'Custom tags' attributes".

        :param dict tags:
        :return:
        """
        self._logger.info("Validating 'Custom Tags' attribute")
        default_tags_count = get_default_tags_count()

        if len(tags) > self.MAX_TAGS_NUMBER:
            raise Exception(
                f"The total number of Azure custom tags must be no more than "
                f"{self.MAX_TAGS_NUMBER - default_tags_count}. "
                f"Present number of custom tags: {len(tags) - default_tags_count}"
            )

    def validate_azure_additional_networks(self, mgmt_networks):
        """Validate 'Additional Mgmt Networks' attribute.

        :param list[str] mgmt_networks:
        :return:
        """
        self._logger.info("Validating Deploy App 'Additional Mgmt Networks' attribute")
        for cidr in mgmt_networks:
            if not is_valid_cidr(cidr):
                msg = (
                    f"CIDR {cidr} under the 'Additional Mgmt Networks' attribute "
                    f"is not in the valid format"
                )
                self._logger.exception(msg)
                raise Exception(msg)

    def validate_deploy_app_add_public_ip(self, deploy_app, connect_subnets):
        """Validate 'Add Public IP' attribute.

        :param deploy_app:
        :param connect_subnets:
        :return:
        """
        self._logger.info("Validating Deploy App 'Add Public IP' attribute")
        all_subnets_are_private = (
            all((not subnet.is_public() for subnet in connect_subnets))
            if connect_subnets
            else False
        )

        if all_subnets_are_private and deploy_app.add_public_ip:
            raise Exception(
                "Cannot deploy App with Public IP when connected "
                "only to private subnets"
            )

    def validate_deploy_app_script_file(self, deploy_app):
        """Validate 'Extension Script file' attribute.

        :param deploy_app:
        :return:
        """
        self._logger.info("Validating Deploy App Extension Script File")

        if not deploy_app.extension_script_file:
            return

        error_msg = (
            f"Unable to retrieve VM Extension Script File: "
            f"{deploy_app.extension_script_file}"
        )

        try:
            response = requests.head(deploy_app.extension_script_file, verify=False)
            response.raise_for_status()
        except Exception:
            self._logger.exception(error_msg)
            raise Exception(error_msg)

    def validate_deploy_app_script_extension(self, deploy_app, image_os):
        """Validate 'Extension Script file' attribute script extension.

        :param deploy_app:
        :param image_os:
        :return:
        """
        self._logger.info("Validating Deploy App Extension Script")

        if not deploy_app.extension_script_file:
            return

        if image_os == OperatingSystemTypes.windows:
            if not deploy_app.extension_script_file.endswith("ps1"):
                raise Exception(
                    "Invalid format for the PowerShell script. "
                    "It must have a 'ps1' extension"
                )
        else:
            if not deploy_app.extension_script_configurations:
                raise Exception(
                    "Linux Custom Script must have a command to execute in "
                    "'Extension Script Configurations' attribute"
                )

    def validate_deploy_app_disk_size(self, deploy_app):
        """Validate 'Disk Size' attribute.

        :param deploy_app:
        :return:
        """
        self._logger.info("Validating Deploy App VM Disk size")

        if not deploy_app.disk_size:
            return

        try:
            disk_size_num = int(deploy_app.disk_size)
        except ValueError:
            error_msg = f"Invalid Virtual Machine Disk size '{deploy_app.disk_size}'"
            self._logger.exception(error_msg)
            raise Exception(error_msg)

        if disk_size_num > self.MAX_VM_DISK_SIZE_GB:
            raise Exception(
                f"Virtual Machine Disk size cannot be larger than "
                f"{self.MAX_VM_DISK_SIZE_GB} GB"
            )

    def validate_vm_size(self, deploy_app_vm_size, cloud_provider_vm_size):
        """Validate 'VM Size' attribute.

        :param str deploy_app_vm_size:
        :param str cloud_provider_vm_size:
        :return:
        """
        self._logger.info("Validating VM size")
        return any([deploy_app_vm_size, cloud_provider_vm_size])
