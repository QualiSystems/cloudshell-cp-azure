from cloudshell.cp.azure.actions.ssh_key_pair import SSHKeyPairActions


class AzureGetAccessKeyFlow:
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

    def get_access_key(self):
        """Get SSH Access Key.

        :return:
        """
        resource_group_name = self._reservation_info.get_resource_group_name()
        storage_account_name = self._reservation_info.get_storage_account_name()

        ssh_keypair_actions = SSHKeyPairActions(
            azure_client=self._azure_client, logger=self._logger
        )

        return ssh_keypair_actions.get_ssh_private_key(
            resource_group_name=resource_group_name,
            storage_account_name=storage_account_name,
        )
