import logging
import typing
from urllib.parse import urlparse

from azure.mgmt.compute import models as compute_models
from msrestazure.azure_exceptions import CloudError

from cloudshell.cp.azure.utils.disks import prepare_full_data_disk_name


class StorageAccountActions:
    def __init__(self, azure_client, logger: logging.Logger):
        """Init command."""
        self._azure_client = azure_client
        self._logger = logger

    def create_storage_account(
        self,
        storage_account_name: str,
        resource_group_name: str,
        region: str,
        tags: typing.Dict[str, str],
    ):
        """Create Storage Account."""
        self._logger.info(f"Creating storage account {storage_account_name}")
        self._azure_client.create_storage_account(
            resource_group_name=resource_group_name,
            region=region,
            storage_account_name=storage_account_name,
            tags=tags,
            wait_for_result=True,
        )

    def get_storage_account(self, storage_account_name: str, resource_group_name: str):
        self._logger.info(f"Getting storage account {storage_account_name}")
        return self._azure_client.get_storage_account(
            resource_group_name=resource_group_name,
            storage_account_name=storage_account_name,
        )

    def get_storage_account_by_name(self, storage_account_name: str):
        self._logger.info(f"Getting storage account {storage_account_name}")
        return self._azure_client.get_storage_account_by_name(
            storage_account_name=storage_account_name
        )

    def delete_storage_account(
        self, storage_account_name: str, resource_group_name: str
    ):
        """Delete Storage Account."""
        self._logger.info(f"Deleting storage account {storage_account_name}")
        self._azure_client.delete_storage_account(
            resource_group_name=resource_group_name,
            storage_account_name=storage_account_name,
        )

    def _parse_blob_url(self, blob_url: str) -> typing.Tuple[str, str, str]:
        """Parses Blob URL into AzureBlobUrlModel.

        :param blob_url: Azure Blob URL ("https://someaccount.blob.core.windows.net/container/blobname")  # noqa: E501
        :rtype: tuple[str, str, str]
        """
        parsed_blob_url = urlparse(blob_url)
        splitted_path = parsed_blob_url.path.split("/")
        blob_name = splitted_path[-1]
        container_name = splitted_path[-2]
        storage_account_name = parsed_blob_url.netloc.split(".", 1)[0]

        return blob_name, container_name, storage_account_name

    def delete_vhd_disk(
        self,
        vhd_url: str,
        resource_group_name: str,
    ):
        """Delete VHD Disk Blob resource on the azure for given VM."""
        self._logger.info(f"Deleting VHD Disk {vhd_url}")
        blob_name, container_name, storage_account_name = self._parse_blob_url(
            blob_url=vhd_url
        )
        self._azure_client.delete_blob(
            blob_name=blob_name,
            container_name=container_name,
            resource_group_name=resource_group_name,
            storage_account_name=storage_account_name,
        )

    def delete_disk(
        self,
        disk_name: str,
        resource_group_name: str,
    ):
        """Delete Managed Disk."""
        self._logger.info(f"Deleting Disk {disk_name}")
        self._azure_client.delete_disk(
            disk_name=disk_name, resource_group_name=resource_group_name
        )

    def create_disk(
        self,
        disk_name: str,
        resource_group_name: str,
        region: str,
        disk_size: str,
        disk_type: str,
        tags: typing.Dict[str, str],
    ):
        """Create Disk."""
        self._logger.info(f"Creating Disk {disk_name}")
        return self._azure_client.create_disk(
            disk_name=disk_name,
            resource_group_name=resource_group_name,
            region=region,
            disk_size=disk_size,
            disk_type=disk_type,
            tags=tags,
        )

    def update_disk(
        self,
        disk: compute_models.Disk,
        resource_group_name: str,
        disk_size: str = None,
        disk_type: str = None,
        tags: typing.Dict[str, str] = None,
    ):
        """Update Disk."""
        self._logger.info(f"Updating Disk {disk.name}")
        return self._azure_client.update_disk(
            disk=disk,
            resource_group_name=resource_group_name,
            disk_size=disk_size,
            disk_type=disk_type,
            tags=tags,
        )

    def get_disk(
        self,
        disk_name: str,
        resource_group_name: str,
    ) -> compute_models.Disk:
        """Get Disk."""
        self._logger.info(f"Getting Disk {disk_name}")
        return self._azure_client.get_disk(
            disk_name=disk_name,
            resource_group_name=resource_group_name,
        )

    def get_vm_data_disk(
        self,
        disk_name: str,
        resource_group_name: str,
        vm_name: str,
    ) -> compute_models.Disk:
        """Get VM Data disk."""
        full_disk_name = prepare_full_data_disk_name(
            disk_name=disk_name, vm_name=vm_name
        )

        for disk_name in (full_disk_name, disk_name):
            try:
                return self.get_disk(
                    disk_name=disk_name, resource_group_name=resource_group_name
                )
            except CloudError:
                self._logger.info(f"Unable to find Disk {disk_name}")

    def create_vm_data_disk(
        self,
        disk_name: str,
        resource_group_name: str,
        vm_name: str,
        region: str,
        disk_size: str,
        disk_type: str,
        tags: typing.Dict[str, str],
    ) -> compute_models.Disk:
        """Create VM Data disk."""
        full_disk_name = prepare_full_data_disk_name(
            disk_name=disk_name, vm_name=vm_name
        )
        return self.create_disk(
            disk_name=full_disk_name,
            resource_group_name=resource_group_name,
            region=region,
            disk_size=disk_size,
            disk_type=disk_type,
            tags=tags,
        )

    def delete_vm_data_disk(
        self,
        disk_name: str,
        resource_group_name: str,
        vm_name: str,
    ):
        """Delete VM Data Disk."""
        full_disk_name = prepare_full_data_disk_name(
            disk_name=disk_name, vm_name=vm_name
        )
        return self.delete_disk(
            disk_name=full_disk_name,
            resource_group_name=resource_group_name,
        )
