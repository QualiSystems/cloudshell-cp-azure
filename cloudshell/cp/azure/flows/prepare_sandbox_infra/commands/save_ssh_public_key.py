from cloudshell.cp.azure.utils.rollback import RollbackCommand


class SaveSSHPublicKeyCommand(RollbackCommand):
    def __init__(
        self,
        rollback_manager,
        cancellation_manager,
        ssh_actions,
        public_key_name,
        resource_group_name,
        public_key,
        region,
        tags,
    ):
        """Init command."""
        super().__init__(
            rollback_manager=rollback_manager, cancellation_manager=cancellation_manager
        )
        self._ssh_actions = ssh_actions
        self._public_key_name = public_key_name
        self._resource_group_name = resource_group_name
        self._public_key = public_key
        self._region = region
        self._tags = tags

    def _execute(self):
        self._ssh_actions.save_ssh_public_key(
            resource_group_name=self._resource_group_name,
            public_key_name=self._public_key_name,
            public_key=self._public_key,
            region=self._region,
            tags=self._tags,
        )

    def rollback(self):
        pass
