from cloudshell.cp.azure.utils.rollback import RollbackCommand


class CreateAllowAdditionalMGMTNetworkRuleCommand(RollbackCommand):
    """Open traffic to VM from Additional MGMT networks."""

    NSG_RULE_PRIORITY = 3000
    NSG_RULE_NAME_TPL = "Allow_{mgmt_network}"

    def __init__(
        self,
        rollback_manager,
        cancellation_manager,
        nsg_actions,
        nsg_name: str,
        vm_name: str,
        mgmt_network,
        vm_resource_group_name: str,
        rules_priority_generator,
    ):
        """Init command."""
        super().__init__(
            rollback_manager=rollback_manager, cancellation_manager=cancellation_manager
        )
        self._nsg_actions = nsg_actions
        self._nsg_name = nsg_name
        self._vm_resource_group_name = vm_resource_group_name
        self._vm_name = vm_name
        self._mgmt_network = mgmt_network
        self._rules_priority_generator = rules_priority_generator

    def _execute(self):
        self._nsg_actions.create_nsg_allow_rule(
            rule_name=self.NSG_RULE_NAME_TPL.format(
                mgmt_network=self._mgmt_network
            ).replace("/", "-"),
            resource_group_name=self._vm_resource_group_name,
            nsg_name=self._nsg_name,
            src_address=self._mgmt_network,
            rule_priority=self._rules_priority_generator.get_priority(
                start_from=self.NSG_RULE_PRIORITY
            ),
        )

    def rollback(self):
        self._nsg_actions.delete_nsg_rule(
            rule_name=self.NSG_RULE_NAME_TPL.format(
                mgmt_network=self._mgmt_network
            ).replace("/", "-"),
            resource_group_name=self._vm_resource_group_name,
            nsg_name=self._nsg_name,
        )
