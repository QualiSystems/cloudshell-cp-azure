import typing

from cloudshell.cp.azure.utils.rollback import RollbackCommand


class CreateDataDiskCommand(RollbackCommand):
    def __init__(
        self,
        rollback_manager,
        cancellation_manager,
        storage_actions,
        disk_model,
        vm_resource_group_name: str,
        region: str,
        vm_name: str,
        tags: typing.Dict[str, str],
    ):
        super().__init__(
            rollback_manager=rollback_manager, cancellation_manager=cancellation_manager
        )
        self._storage_actions = storage_actions
        self._disk_model = disk_model
        self._vm_resource_group_name = vm_resource_group_name
        self._region = region
        self._vm_name = vm_name
        self._tags = tags

    def _execute(self):
        return self._storage_actions.create_vm_data_disk(
            disk_name=self._disk_model.name,
            resource_group_name=self._vm_resource_group_name,
            vm_name=self._vm_name,
            region=self._region,
            disk_size=self._disk_model.disk_size,
            disk_type=self._disk_model.disk_type or self._disk_model.DEFAULT_DISK_TYPE,
            tags=self._tags,
        )

    def rollback(self):
        return self._storage_actions.delete_vm_data_disk(
            disk_name=self._disk_model.name,
            resource_group_name=self._vm_resource_group_name,
            vm_name=self._vm_name,
        )
