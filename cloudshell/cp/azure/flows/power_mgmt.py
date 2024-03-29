from cloudshell.cp.azure.actions.vm import VMActions


class AzurePowerManagementFlow:
    def __init__(self, resource_config, azure_client, reservation_info, logger):
        """Init command.

        :param resource_config:
        :param azure_client:
        :param reservation_info:
        :param logging.Logger logger:
        """
        self._resource_config = resource_config
        self._azure_client = azure_client
        self._reservation_info = reservation_info
        self._logger = logger

    def power_on(self, deployed_app):
        """Power On VM.

        :param deployed_app:
        :return:
        """
        sandbox_resource_group_name = self._reservation_info.get_resource_group_name()
        vm_resource_group_name = (
            deployed_app.resource_group_name or sandbox_resource_group_name
        )

        vm_actions = VMActions(azure_client=self._azure_client, logger=self._logger)
        vm_actions.start_vm(
            vm_name=deployed_app.name, resource_group_name=vm_resource_group_name
        )

    def power_off(self, deployed_app):
        """Power Off VM.

        :param deployed_app:
        :return:
        """
        sandbox_resource_group_name = self._reservation_info.get_resource_group_name()
        vm_resource_group_name = (
            deployed_app.resource_group_name or sandbox_resource_group_name
        )

        vm_actions = VMActions(azure_client=self._azure_client, logger=self._logger)
        vm_actions.stop_vm(
            vm_name=deployed_app.name, resource_group_name=vm_resource_group_name
        )
