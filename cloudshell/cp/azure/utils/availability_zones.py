from typing import List


class AzureZonesManager:
    DEFAULT_APP_ZONES_VALUE = ["Inherited"]

    def __init__(self, resource_config):
        """Init command."""
        self._resource_config = resource_config

    def get_resource_zones(self):
        """Get Availability Zones from the AzureCloudProvider Resource."""
        zones = self._resource_config.availability_zones
        if zones:
            return [zone.strip() for zone in zones.split(",")]
        else:
            return []

    def get_availability_zones(self, zones: List):
        """Get Key Vault Name for the VM-related objects."""
        if zones != self.DEFAULT_APP_ZONES_VALUE:
            return zones

        return self.get_resource_zones()
