from cloudshell.shell.standards.core.resource_config_entities import (
    GenericResourceConfig,
    PasswordAttrRO,
    ResourceAttrRO,
)

from cloudshell.cp.azure.exceptions import InvalidAttrException


class RegionResourceAttrRO(ResourceAttrRO):
    def __get__(self, instance, owner):
        """Get Region resource attribute.

        :param GenericResourceConfig instance:
        :rtype: str
        """
        if instance is None:
            return self

        attr = instance.attributes.get(self.get_key(instance), self.default)
        return attr.lower().replace(" ", "")


class AdditionalMgmtNetworksAttrRO(ResourceAttrRO):
    def __get__(self, instance, owner):
        """Get Additional MGM Networks resource attribute.

        :param GenericResourceConfig instance:
        :rtype: str
        """
        if instance is None:
            return self

        attr = instance.attributes.get(self.get_key(instance), self.default)
        if attr:
            return [param.strip() for param in attr.split(",")]

        return []


class CustomTagsAttrRO(ResourceAttrRO):
    def __get__(self, instance, owner):
        """Get Custom Tags resource attribute.

        :param GenericResourceConfig instance:
        :rtype: str
        """
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


class AzureResourceConfig(GenericResourceConfig):
    region = RegionResourceAttrRO("Region", RegionResourceAttrRO.NAMESPACE.SHELL_NAME)

    vm_size = ResourceAttrRO("VM Size", ResourceAttrRO.NAMESPACE.SHELL_NAME)

    networks_in_use = ResourceAttrRO(
        "Networks in use", ResourceAttrRO.NAMESPACE.SHELL_NAME
    )

    azure_subscription_id = ResourceAttrRO(
        "Azure Subscription ID", ResourceAttrRO.NAMESPACE.SHELL_NAME
    )

    azure_tenant_id = ResourceAttrRO(
        "Azure Tenant ID", ResourceAttrRO.NAMESPACE.SHELL_NAME
    )

    azure_application_id = ResourceAttrRO(
        "Azure Application ID", ResourceAttrRO.NAMESPACE.SHELL_NAME
    )

    azure_application_key = PasswordAttrRO(
        "Azure Application Key", PasswordAttrRO.NAMESPACE.SHELL_NAME
    )

    management_group_name = ResourceAttrRO(
        "Management Group Name", ResourceAttrRO.NAMESPACE.SHELL_NAME
    )

    execution_server_selector = ResourceAttrRO(
        "Execution Server Selector", ResourceAttrRO.NAMESPACE.SHELL_NAME
    )

    additional_mgmt_networks = AdditionalMgmtNetworksAttrRO(
        "Additional Mgmt Networks", AdditionalMgmtNetworksAttrRO.NAMESPACE.SHELL_NAME
    )

    custom_tags = CustomTagsAttrRO("Custom Tags", CustomTagsAttrRO.NAMESPACE.SHELL_NAME)

    private_ip_allocation_method = ResourceAttrRO(
        "Private IP Allocation Method", ResourceAttrRO.NAMESPACE.SHELL_NAME
    )

    @classmethod
    def from_context(cls, shell_name, context, api=None, supported_os=None):
        """Creates an instance of a Resource by given context.

        :param str shell_name: Shell Name
        :param list supported_os: list of supported OS
        :param cloudshell.shell.core.driver_context.ResourceCommandContext context:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession api:
        :rtype: GenericResourceConfig
        """
        return cls(
            shell_name=shell_name,
            name=context.resource.name,
            fullname=context.resource.fullname,
            address=context.resource.address,
            family_name=context.resource.family,
            attributes=dict(context.resource.attributes),
            supported_os=supported_os,
            api=api,
        )
