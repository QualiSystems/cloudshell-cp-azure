class AzureTagsManager:
    class DefaultTagNames:
        created_by = "CreatedBy"
        owner = "Owner"
        blueprint = "Blueprint"
        sandbox_id = "SandboxId"
        domain = "Domain"
        vm_name = "Name"

    class DefaultTagValues:
        created_by = "CloudShell"

    def __init__(self, reservation_info, resource_config):
        """Init command.

        :param reservation_info:
        :param resource_config:
        """
        self._reservation_info = reservation_info
        self._resource_config = resource_config

    def get_default_tags(self):
        """Get pre-defined CloudShell tags.

        :return:
        """
        return {
            self.DefaultTagNames.created_by: self.DefaultTagValues.created_by,
            self.DefaultTagNames.owner: self._reservation_info.owner,
            self.DefaultTagNames.blueprint: self._reservation_info.blueprint,
            self.DefaultTagNames.sandbox_id: self._reservation_info.reservation_id,
            self.DefaultTagNames.domain: self._reservation_info.domain,
        }

    def get_reservation_tags(self):
        """Get tags for the reservation-related objects.

        :return:
        """
        tags = self.get_default_tags()
        tags.update(self._resource_config.custom_tags)

        return tags

    def get_vm_tags(self, vm_name, extended_custom_tags=None):
        """Get tags for the VM-related objects.

        :param str vm_name:
        :param dict extended_custom_tags:
        :return:
        """
        tags = self.get_reservation_tags()

        tags[self.DefaultTagNames.vm_name] = vm_name

        if extended_custom_tags is not None:
            tags.update(extended_custom_tags)

        return tags


def get_default_tags_count():
    return len(
        [
            tag_name
            for tag_name in vars(AzureTagsManager.DefaultTagNames)
            if not tag_name.startswith("__")
        ]
    )
