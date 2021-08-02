import typing

from azure.mgmt.compute.models import OperatingSystemTypes

from cloudshell.cp.azure.utils.rollback import RollbackCommand


class CreateVMExtensionCommand(RollbackCommand):
    def __init__(
        self,
        rollback_manager,
        cancellation_manager,
        task_waiter_manager,
        vm_extension_actions,
        script_file_path: str,
        script_config: str,
        timeout: int,
        image_os_type: str,
        region: str,
        vm_resource_group_name: str,
        vm_name: str,
        tags: typing.Dict[str, str],
    ):
        """Init command."""
        super().__init__(
            rollback_manager=rollback_manager, cancellation_manager=cancellation_manager
        )
        self._task_waiter_manager = task_waiter_manager
        self._vm_extension_actions = vm_extension_actions
        self._script_file_path = script_file_path
        self._script_config = script_config
        self._timeout = timeout
        self._image_os_type = image_os_type
        self._region = region
        self._vm_resource_group_name = vm_resource_group_name
        self._vm_name = vm_name
        self._tags = tags

    def _execute(self):
        if self._image_os_type == OperatingSystemTypes.linux:
            operation_poller = self._vm_extension_actions.create_linux_vm_script_extension(  # noqa: E501
                region=self._region,
                resource_group_name=self._vm_resource_group_name,
                vm_name=self._vm_name,
                script_file_path=self._script_file_path,
                script_config=self._script_config,
                tags=self._tags,
            )
        else:
            operation_poller = self._vm_extension_actions.create_windows_vm_script_extension(  # noqa: E501
                region=self._region,
                resource_group_name=self._vm_resource_group_name,
                vm_name=self._vm_name,
                script_file_path=self._script_file_path,
                script_config=self._script_config,
                tags=self._tags,
            )

        return self._task_waiter_manager.wait_for_task(
            operation_poller, timeout=self._timeout
        )

    def rollback(self):
        pass
