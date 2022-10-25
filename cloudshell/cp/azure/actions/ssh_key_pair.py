from typing import Dict

from cloudshell.cp.core.utils import generate_ssh_key_pair

from cloudshell.cp.azure.exceptions import ResourceNotFoundException


class SSHKeyPairActions:
    SSH_FILE_SHARE_NAME = "sshkeypair"
    SSH_FILE_SHARE_DIRECTORY = ""
    SSH_PUB_KEY_NAME = "id_rsa.pub"
    SSH_PRIVATE_KEY_NAME = "id_rsa"

    def __init__(self, azure_client, logger):
        """Init command."""
        self._azure_client = azure_client
        self._logger = logger

    def create_ssh_key_pair(self):
        """Create SSH Key Pair."""
        self._logger.info("Creating SSH key pair...")
        return generate_ssh_key_pair()

    def save_ssh_public_key(
        self,
        resource_group_name: str,
        public_key_name: str,
        public_key: str,
        region: str,
        tags: Dict[str, str],
    ):
        """Save SSH Pubic Key on the Azure Storage."""
        self._logger.info("Saving SSH public key on the Azure...")
        self._azure_client.set_ssh_key(
            key_name=public_key_name,
            key_value=public_key,
            region=region,
            tags=tags,
            resource_group_name=resource_group_name,
        )

    def get_ssh_public_key(
        self,
        public_key_name: str,
        resource_group_name: str,
        storage_account_name: str,
    ) -> str:
        """Get SSH Pubic Key from Azure SSH Keys or the Azure Storage."""
        self._logger.info("Getting SSH public key from the Azure...")

        try:
            public_key = self._azure_client.get_ssh_key(
                key_name=public_key_name,
                resource_group_name=resource_group_name,
            ).public_key
        except ResourceNotFoundException:
            self._logger.debug(
                "Could not find SSH public key inside Azure SSH Keys."
                "Trying to get SSH public key from Azure Storage."
            )
            public_key = self._azure_client.get_file(
                resource_group_name=resource_group_name,
                storage_account_name=storage_account_name,
                share_name=self.SSH_FILE_SHARE_NAME,
                directory_name=self.SSH_FILE_SHARE_DIRECTORY,
                file_name=self.SSH_PUB_KEY_NAME,
            )

        return public_key

    def delete_ssh_public_key(self, public_key_name: str, resource_group_name: str):
        """Delete SSH Pubic Key from Azure SSH Keys."""
        self._logger.info("Removing SSH public key from the Azure...")
        self._azure_client.delete_ssh_key(
            key_name=public_key_name,
            resource_group_name=resource_group_name,
        )

    def save_ssh_private_key(
        self,
        key_vault_name: str,
        private_key_name: str,
        private_key: str,
        tags: Dict[str, str],
    ):
        """Save SSH Private Key on the Azure Key Vault."""
        self._logger.info("Saving SSH private key on the Azure...")

        self._azure_client.set_key_vault_secret(
            key_vault_name=key_vault_name,
            secret_name=private_key_name,
            secret_value=private_key,
            tags=tags,
        )

    def get_ssh_private_key(
        self,
        key_vault_name: str,
        private_key_name: str,
        resource_group_name: str,
        storage_account_name: str,
    ) -> str:
        """Get SSH Private Key from Azure Key Vault or the Azure Storage."""
        self._logger.info("Getting SSH private key from the Azure...")
        try:
            private_key = self._azure_client.get_key_vault_secret(
                key_vault_name=key_vault_name,
                secret_name=private_key_name,
            )
        except ResourceNotFoundException:
            self._logger.debug(
                "Could not find SSH private key in Azure Key Vault."
                "Trying to get SSH private key from Azure Storage."
            )
            private_key = self._azure_client.get_file(
                resource_group_name=resource_group_name,
                storage_account_name=storage_account_name,
                share_name=self.SSH_FILE_SHARE_NAME,
                directory_name=self.SSH_FILE_SHARE_DIRECTORY,
                file_name=self.SSH_PRIVATE_KEY_NAME,
            )

        return private_key

    def delete_ssh_private_key(self, key_vault_name: str, private_key_name: str):
        """Delete SSH Private Key from Azure Key Vault."""
        self._logger.info("Removing SSH private key from the Azure Key Vault...")
        self._azure_client.delete_key_vault_secret(
            key_vault_name=key_vault_name,
            secret_name=private_key_name,
        )
