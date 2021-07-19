from azure.mgmt.compute import models as compute_models

from cloudshell.cp.azure.actions.storage_account import StorageAccountActions
from cloudshell.cp.azure.actions.vm import VMActions
from cloudshell.cp.azure.flows.reconfigure_vm import commands
from cloudshell.cp.azure.utils.azure_task_waiter import AzureTaskWaiter
from cloudshell.cp.azure.utils.disks import (
    get_azure_disk_type,
    get_disk_lun_generator,
    parse_data_disks_input,
)
from cloudshell.cp.azure.utils.rollback import RollbackCommandsManager
from cloudshell.cp.azure.utils.tags import AzureTagsManager


class AzureReconfigureVMFlow:
    def __init__(
        self,
        resource_config,
        azure_client,
        cs_api,
        reservation_info,
        cancellation_manager,
        logger,
    ):
        """Init command.

        :param resource_config:
        :param azure_client:
        :param cs_api:
        :param reservation_info:
        :param cancellation_manager:
        :param logging.Logger logger:
        """
        self._resource_config = resource_config
        self._azure_client = azure_client
        self._cs_api = cs_api
        self._reservation_info = reservation_info
        self._cancellation_manager = cancellation_manager
        self._logger = logger
        self._rollback_manager = RollbackCommandsManager(logger=self._logger)
        self._task_waiter_manager = AzureTaskWaiter(
            cancellation_manager=self._cancellation_manager, logger=self._logger
        )
        self._tags_manager = AzureTagsManager(
            reservation_info=self._reservation_info, resource_config=resource_config
        )

    def _process_os_disk(self, os_disk_size, os_disk_type, vm, resource_group_name):
        """Update OS Disk."""
        storage_actions = StorageAccountActions(
            azure_client=self._azure_client, logger=self._logger
        )
        os_disk_type = get_azure_disk_type(os_disk_type) if os_disk_type else None

        os_disk = storage_actions.get_disk(
            disk_name=vm.storage_profile.os_disk.name,
            resource_group_name=resource_group_name,
        )

        storage_actions.update_disk(
            disk=os_disk,
            resource_group_name=resource_group_name,
            disk_size=os_disk_size,
            disk_type=os_disk_type,
        )

    def _process_data_disks(self, data_disks, vm, resource_group_name):
        """Add/Update VM Data disks."""
        storage_actions = StorageAccountActions(
            azure_client=self._azure_client, logger=self._logger
        )
        tags = self._tags_manager.get_vm_tags(vm_name=vm.name)

        disk_models = parse_data_disks_input(data_disks)
        lun_generator = get_disk_lun_generator(
            existing_disks=vm.storage_profile.data_disks
        )

        for disk_model in disk_models:
            disk = storage_actions.get_vm_data_disk(
                disk_name=disk_model.name,
                resource_group_name=resource_group_name,
                vm_name=vm.name,
            )

            if disk:
                storage_actions.update_disk(
                    disk=disk,
                    resource_group_name=resource_group_name,
                    disk_size=disk_model.disk_size,
                    disk_type=disk_model.disk_type,
                    tags=tags,
                )
            else:
                disk = commands.CreateDataDiskCommand(
                    rollback_manager=self._rollback_manager,
                    cancellation_manager=self._cancellation_manager,
                    storage_actions=storage_actions,
                    disk_model=disk_model,
                    resource_group_name=resource_group_name,
                    region=self._resource_config.region,
                    vm_name=vm.name,
                    tags=tags,
                ).execute()

                vm.storage_profile.data_disks.append(
                    compute_models.DataDisk(
                        lun=next(lun_generator),
                        name=disk.name,
                        create_option=compute_models.DiskCreateOptionTypes.attach,
                        managed_disk=compute_models.ManagedDiskParameters(id=disk.id),
                    )
                )

    def reconfigure(
        self, deployed_app, vm_size, os_disk_size, os_disk_type, data_disks
    ):
        """Change VM Size and Data Disks."""
        resource_group_name = self._reservation_info.get_resource_group_name()
        vm_actions = VMActions(azure_client=self._azure_client, logger=self._logger)

        vm = vm_actions.get_vm(
            vm_name=deployed_app.name, resource_group_name=resource_group_name
        )

        if vm_size:
            vm.hardware_profile.vm_size = vm_size

        with self._rollback_manager:
            if data_disks:
                self._process_data_disks(
                    data_disks=data_disks,
                    vm=vm,
                    resource_group_name=resource_group_name,
                )

            if any([os_disk_size, os_disk_type]):
                self._process_os_disk(
                    os_disk_size=os_disk_size,
                    os_disk_type=os_disk_type,
                    vm=vm,
                    resource_group_name=resource_group_name,
                )

            operation_poller = vm_actions.start_create_or_update_vm_task(
                vm_name=vm.name,
                virtual_machine=vm,
                resource_group_name=resource_group_name,
            )

            self._task_waiter_manager.wait_for_task(operation_poller)