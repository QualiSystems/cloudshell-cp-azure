from cloudshell.cp.core.reservation_info import ReservationInfo


class AzureReservationInfo(ReservationInfo):
    SANDBOX_NSG_NAME_TPL = "NSG_sandbox_all_subnets_{reservation_id}"

    def get_resource_group_name(self):
        """Get Resource Group name.

        :rtype: str
        """
        return self.reservation_id

    def get_storage_account_name(self):
        """Get Storage Account name.

        In azure it must be between 3-24 chars. Dashes are not allowed as well.
        :rtype: str
        """
        return self.reservation_id.replace("-", "")[:24]

    def get_network_security_group_name(self):
        """Get Network Security Group name.

        :rtype: str
        """
        return self.SANDBOX_NSG_NAME_TPL.format(reservation_id=self.reservation_id)
