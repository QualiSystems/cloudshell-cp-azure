from cloudshell.cp.azure.utils.rollback import RollbackCommand


class SaveSSHPrivateKeyCommand(RollbackCommand):
    def __init__(
        self,
        rollback_manager,
        cancellation_manager,
        ssh_actions,
        key_vault_name,
        private_key_name,
        private_key,
        tags,
    ):
        """Init command."""
        super().__init__(
            rollback_manager=rollback_manager, cancellation_manager=cancellation_manager
        )
        self._ssh_actions = ssh_actions
        self._key_vault_name = key_vault_name
        self._private_key_name = private_key_name
        self._private_key = private_key
        self._tags = tags

    def _execute(self):
        self._ssh_actions.save_ssh_private_key(
            key_vault_name=self._key_vault_name,
            private_key_name=self._private_key_name,
            private_key=self._private_key,
            tags=self._tags,
        )

    def rollback(self):
        pass
