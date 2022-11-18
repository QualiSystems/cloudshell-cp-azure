import re

from azure.mgmt.network.models import SecurityRuleProtocol

from cloudshell.cp.azure.utils.rollback import RollbackCommand


class CreateAllowVMInboundPortRuleCommand(RollbackCommand):
    """Open traffic to VM on inbound ports (an attribute on the App) on the VM NSG."""

    PORT_DATA_MATCH = re.compile(
        r"^(?P<from_port>\d+)"
        r"(-(?P<to_port>\d+))?"
        r"(:(?P<protocol>(udp|tcp|icmp)))?"
        r"(:(?P<destination>\S+))?$",
        re.IGNORECASE,
    )
    ICMP_PORT_DATA_MATCH = re.compile(
        r"^(?P<protocol>icmp)" r"(:(?P<destination>\S+))?$",
        re.IGNORECASE,
    )
    DEFAULT_DESTINATION = SecurityRuleProtocol.asterisk
    DEFAULT_PROTOCOL = "tcp"

    NSG_RULE_PRIORITY = 1000
    NSG_RULE_NAME_TPL = "{vm_name}_inbound_port:{port_range}:{protocol}-{priority}"

    def __init__(
        self,
        rollback_manager,
        cancellation_manager,
        nsg_actions,
        nsg_name: str,
        vm_name: str,
        inbound_port,
        resource_group_name: str,
        rules_priority_generator,
    ):
        """Init command."""
        super().__init__(
            rollback_manager=rollback_manager, cancellation_manager=cancellation_manager
        )
        self._nsg_actions = nsg_actions
        self._nsg_name = nsg_name
        self._vm_name = vm_name
        self._inbound_port = inbound_port
        self._resource_group_name = resource_group_name
        self._rules_priority_generator = rules_priority_generator
        self._port_range, self._protocol, self._cidr = self._parse_port_range(
            self._inbound_port
        )

    def _execute(self):
        rule_priority = self._rules_priority_generator.get_priority(
            start_from=self.NSG_RULE_PRIORITY
        )
        self._nsg_actions.create_nsg_allow_rule(
            rule_name=self.NSG_RULE_NAME_TPL.format(
                vm_name=self._vm_name,
                port_range=self._port_range,
                protocol=self._protocol,
                priority=rule_priority,
            ),
            resource_group_name=self._resource_group_name,
            nsg_name=self._nsg_name,
            dst_port_range=self._port_range,
            dst_address=self._cidr,
            protocol=self._protocol,
            rule_priority=rule_priority,
        )

    def _parse_port_range(self, port_data):
        match = self.PORT_DATA_MATCH.search(port_data)
        if match:
            from_port = match.group("from_port")
            to_port = match.group("to_port")
        else:
            match = self.ICMP_PORT_DATA_MATCH.search(port_data)
            if match:
                from_port = to_port = "-1"
            else:
                msg = f"The value '{port_data}' is not a valid ports rule"
                raise ValueError(msg)

        destination = match.group("destination") or self.DEFAULT_DESTINATION
        protocol = match.group("protocol") or self.DEFAULT_PROTOCOL
        port = f"{from_port}"
        if to_port:
            port = f"{from_port}-{to_port}"
        return port, protocol, destination

    def rollback(self):
        self._nsg_actions.delete_nsg_rule(
            rule_name=self.NSG_RULE_NAME_TPL.format(
                vm_name=self._vm_name,
                port_range=self._port_range,
                protocol=self._protocol,
            ),
            resource_group_name=self._resource_group_name,
            nsg_name=self._nsg_name,
        )
