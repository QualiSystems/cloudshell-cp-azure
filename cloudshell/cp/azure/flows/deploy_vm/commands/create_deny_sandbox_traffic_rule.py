from cloudshell.cp.azure.utils.rollback import RollbackCommand


class CreateDenySandoxTrafficRuleCommand(RollbackCommand):
    """Block traffic from the Sandbox if "Allow All Sandbox Traffic" is False."""

    NSG_RULE_PRIORITY = 4090
    NSG_RULE_NAME_TPL = "Deny_Sandbox_Traffic"
    VIRTUAL_NETWORK_SRC_ADDRESS = "VirtualNetwork"

    def __init__(
        self,
        rollback_manager,
        cancellation_manager,
        nsg_actions,
        nsg_name,
        vm_resource_group_name,
        rules_priority_generator,
    ):
        """Init command."""
        super().__init__(
            rollback_manager=rollback_manager, cancellation_manager=cancellation_manager
        )
        self._nsg_actions = nsg_actions
        self._nsg_name = nsg_name
        self._vm_resource_group_name = vm_resource_group_name
        self._rules_priority_generator = rules_priority_generator

    def _execute(self):
        self._nsg_actions.create_nsg_deny_rule(
            rule_name=self.NSG_RULE_NAME_TPL,
            resource_group_name=self._vm_resource_group_name,
            nsg_name=self._nsg_name,
            src_address=self.VIRTUAL_NETWORK_SRC_ADDRESS,
            rule_priority=self._rules_priority_generator.get_priority(
                start_from=self.NSG_RULE_PRIORITY
            ),
        )

    def rollback(self):
        self._nsg_actions.delete_nsg_rule(
            rule_name=self.NSG_RULE_NAME_TPL,
            resource_group_name=self._vm_resource_group_name,
            nsg_name=self._nsg_name,
        )
