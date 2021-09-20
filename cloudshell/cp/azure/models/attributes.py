from cloudshell.shell.standards.core.resource_config_entities import ResourceAttrRO

from cloudshell.cp.azure.exceptions import (
    InvalidAttrException,
    InvalidDiskTypeException,
)
from cloudshell.cp.azure.utils.disks import parse_data_disks_input


class InboundPortsAttrRO(ResourceAttrRO):
    def __get__(self, instance, owner):
        if instance is None:
            return self

        attr = instance.attributes.get(self.get_key(instance), self.default)
        return [port_data.strip() for port_data in attr.split(";") if port_data]


class DataDisksAttrRO(ResourceAttrRO):
    def __get__(self, instance, owner):
        if instance is None:
            return self

        attr = instance.attributes.get(self.get_key(instance), self.default)

        try:
            disks = parse_data_disks_input(attr)
        except InvalidDiskTypeException as e:
            raise InvalidAttrException(
                "'Data Disks' attribute is in incorrect format"
            ) from e

        return disks


class CustomTagsAttrRO(ResourceAttrRO):
    def __get__(self, instance, owner):
        if instance is None:
            return self

        attr = instance.attributes.get(self.get_key(instance), self.default)
        if attr:
            try:
                return {
                    tag_key.strip(): tag_val.strip()
                    for tag_key, tag_val in [
                        tag_data.split("=") for tag_data in attr.split(";") if tag_data
                    ]
                }
            except ValueError:
                raise InvalidAttrException(
                    "'Custom Tags' attribute is in incorrect format"
                )

        return {}


class IntegerAttrRO(ResourceAttrRO):
    def __get__(self, instance, owner):
        if instance is None:
            return self

        attr = instance.attributes.get(self.get_key(instance), self.default)
        return int(attr) if attr else None
