class VMImageActions:
    def __init__(self, azure_client, logger):
        """Init command.

        :param cloudshell.cp.azure.azure_client.AzureAPIClient azure_client:
        :param logging.Logger logger:
        """
        self._azure_client = azure_client
        self._logger = logger

    def get_marketplace_image_os(self, region, publisher_name, offer, sku):
        """Get marketplace image OS.

        :param str region:
        :param str publisher_name:
        :param str offer:
        :param str sku:
        :return:
        """
        self._logger.info(
            f"Getting Marketplace Image OS for Publisher: {publisher_name}, "
            f"Offer: {offer}, SKU: {sku}"
        )
        image = self._azure_client.get_latest_virtual_machine_image(
            region=region, publisher_name=publisher_name, offer=offer, sku=sku
        )
        return image.os_disk_image.operating_system

    def get_custom_image_os(self, image_resource_group_name, image_name):
        """Get custom image OS.

        :param str image_resource_group_name:
        :param str image_name:
        :return:
        """
        self._logger.info(f"Getting Custom Image OS for Image: {image_name}")
        image = self._azure_client.get_custom_virtual_machine_image(
            image_name=image_name, resource_group_name=image_resource_group_name
        )
        return image.storage_profile.os_disk.os_type

    def get_custom_image_id(self, image_resource_group_name, image_name):
        """Get custom image ID.

        :param str image_resource_group_name:
        :param str image_name:
        :return:
        """
        self._logger.info(f"Getting Custom Image ID for Image: {image_name}")
        image = self._azure_client.get_custom_virtual_machine_image(
            image_name=image_name, resource_group_name=image_resource_group_name
        )
        return image.id

    def get_gallery_image_os(
        self, gallery_name, gallery_image_name, resource_group, subscription_id
    ):
        """Get gallery image os.

        :param gallery_name:
        :param gallery_image_name:
        :param resource_group:
        :param subscription_id:
        :return:
        """
        self._logger.info(
            f"Getting image OS for image {gallery_image_name}, "
            f"from Shared Gallery {gallery_name}"
        )
        image = self._azure_client.get_gallery_machine_image(
            resource_group=resource_group,
            gallery_name=gallery_name,
            gallery_image_name=gallery_image_name,
            subscription_id=subscription_id,
        )
        return image.os_type

    def get_gallery_image_id(
        self,
        gallery_name,
        gallery_image_name,
        gallery_image_version,
        resource_group,
        subscription_id,
    ):
        """Get gallery image id.

        :param gallery_name:
        :param gallery_image_name:
        :param gallery_image_version:
        :param resource_group:
        :param subscription_id:
        :return:
        """
        self._logger.info(
            f"Getting image ID for image {gallery_image_name}:{gallery_image_version}, "
            f"from Shared Gallery {gallery_name}"
        )
        if gallery_image_version and gallery_image_version != "latest":
            image = self._azure_client.get_gallery_machine_image_version(
                resource_group=resource_group,
                gallery_name=gallery_name,
                gallery_image_name=gallery_image_name,
                gallery_image_version=gallery_image_version,
                subscription_id=subscription_id,
            )
        else:
            image = self._azure_client.get_gallery_machine_image(
                resource_group=resource_group,
                gallery_name=gallery_name,
                gallery_image_name=gallery_image_name,
                subscription_id=subscription_id,
            )
        return image.id
