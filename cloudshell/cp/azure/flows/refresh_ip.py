import logging

from cloudshell.cp.azure.actions.network import NetworkActions
from cloudshell.cp.azure.actions.vm import VMActions
from cloudshell.cp.azure.utils.azure_name_parser import get_name_from_resource_id


class AzureRefreshIPFlow:
    def __init__(
        self,
        resource_config,
        azure_client,
        cs_api,
        reservation_info,
        cancellation_manager,
        logger: logging.Logger,
    ):
        """Init command."""
        self._resource_config = resource_config
        self._azure_client = azure_client
        self._cs_api = cs_api
        self._reservation_info = reservation_info
        self._cancellation_manager = cancellation_manager
        self._logger = logger

    @staticmethod
    def _get_primary_vm_interface(vm):
        """Get primary VM interface."""
        for interface in vm.network_profile.network_interfaces:
            if interface.primary:
                return interface

        return vm.network_profile.network_interfaces[0]

    def refresh_ip(self, deployed_app):
        """Refresh Public and Private IPs on the CloudShell resource."""
        sandbox_resource_group_name = self._reservation_info.get_resource_group_name()
        vm_resource_group_name = (
            deployed_app.resource_group_name or sandbox_resource_group_name
        )

        vm_actions = VMActions(azure_client=self._azure_client, logger=self._logger)
        network_actions = NetworkActions(
            azure_client=self._azure_client, logger=self._logger
        )

        vm = vm_actions.get_active_vm(
            vm_name=deployed_app.name, resource_group_name=vm_resource_group_name
        )

        primary_interface_ref = self._get_primary_vm_interface(vm)
        interface_name = get_name_from_resource_id(primary_interface_ref.id)

        vm_network = network_actions.get_vm_network(
            interface_name=interface_name, resource_group_name=vm_resource_group_name
        )

        vm_ip_configuration = vm_network.ip_configurations[0]
        private_ip_on_azure = vm_ip_configuration.private_ip_address
        public_ip_reference = vm_ip_configuration.public_ip_address

        if public_ip_reference is None:
            self._logger.info(
                f"There is no Public IP attached to the VM {deployed_app.name}"
            )
            public_ip_on_azure = ""
        else:
            self._logger.info(f"Retrieving Public IP for the VM {deployed_app.name}")
            pub_ip_addr = network_actions.get_vm_network_public_ip(
                interface_name=interface_name,
                resource_group_name=vm_resource_group_name,
            )
            public_ip_on_azure = pub_ip_addr.ip_address

        self._logger.info(f"Public IP on Azure: {public_ip_on_azure}")
        self._logger.info(f"Public IP on CloudShell: {deployed_app.public_ip}")

        if public_ip_on_azure != deployed_app.public_ip:
            self._logger.info(
                f"Updating Public IP on the VM {deployed_app.name} "
                f"to {public_ip_on_azure}"
            )
            deployed_app.update_public_ip(public_ip_on_azure)

        self._logger.info(f"Private IP on Azure: {private_ip_on_azure}")
        self._logger.info(f"Private IP on CloudShell: {deployed_app.private_ip}")

        if private_ip_on_azure != deployed_app.private_ip:
            self._logger.info(
                f"Updating Private IP on the resource to {private_ip_on_azure}"
            )
            self._cs_api.UpdateResourceAddress(
                resourceFullPath=deployed_app.name, resourceAddress=private_ip_on_azure
            )
