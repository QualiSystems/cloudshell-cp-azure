import typing

from cloudshell.cp.azure.utils.rollback import RollbackCommand


class CreateVMNSGCommand(RollbackCommand):
    def __init__(
        self,
        rollback_manager,
        cancellation_manager,
        nsg_actions,
        vm_name: str,
        vm_resource_group_name: str,
        region: str,
        tags: typing.Dict[str, str],
    ):
        """Init command."""
        super().__init__(
            rollback_manager=rollback_manager, cancellation_manager=cancellation_manager
        )
        self._nsg_actions = nsg_actions
        self._vm_name = vm_name
        self._vm_resource_group_name = vm_resource_group_name
        self._region = region
        self._tags = tags

    def _execute(self):
        return self._nsg_actions.create_vm_network_security_group(
            vm_name=self._vm_name,
            resource_group_name=self._vm_resource_group_name,
            region=self._region,
            tags=self._tags,
        )

    def rollback(self):
        return self._nsg_actions.delete_vm_network_security_group(
            vm_name=self._vm_name, resource_group_name=self._vm_resource_group_name
        )
