import time
from datetime import datetime, timedelta

from cloudshell.cp.azure.exceptions import AzureTaskTimeoutException


class AzureTaskWaiter:
    DEFAULT_WAIT_TIME = 30
    DEFAULT_TIMEOUT = 30 * 60

    def __init__(self, cancellation_manager, logger):
        """Init command.

        :param cancellation_manager:
        :param logging.Logger logger:
        """
        self._cancellation_manager = cancellation_manager
        self._logger = logger

    def wait_for_task(
        self,
        operation_poller,
        timeout=None,
        wait_time=None,
        azure_client=None,
        vm_name=None,
        resource_group_name=None,
    ):
        """Wait for Azure task to be processed.

        :param msrestazure.azure_operation.AzureOperationPoller operation_poller:
        :param int timeout:
        :param int wait_time:
        :param AzureAPIClient azure_client:
        :param str vm_name:
        :param str resource_group_name:
        """
        wait_time = wait_time or self.DEFAULT_WAIT_TIME
        timeout = timeout or self.DEFAULT_TIMEOUT
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while not operation_poller.done():
            with self._cancellation_manager:
                self._logger.info(
                    f"Waiting for operation to complete, current status is "
                    f"{operation_poller.status()}"
                )

                if azure_client and vm_name and resource_group_name:
                    vm_statuses = (
                        azure_client._compute_client.virtual_machines.instance_view(
                            resource_group_name=resource_group_name, vm_name=vm_name
                        ).statuses
                    )
                    if len(vm_statuses) >= 2:
                        if vm_statuses[0].code == "ProvisioningState/succeeded" or (
                            vm_statuses[0].code == "ProvisioningState/creating"
                            and vm_statuses[1].code == "PowerState/running"
                        ):
                            self._logger.info("VM provisioning finished successfully.")
                            return azure_client.get_vm(
                                resource_group_name=resource_group_name, vm_name=vm_name
                            )

                time.sleep(wait_time)

            if datetime.now() > timeout_time:
                raise AzureTaskTimeoutException(
                    f"Unable to perform operation within {timeout / 60} minute(s)"
                )

        return operation_poller.result()
