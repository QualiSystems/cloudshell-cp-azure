class AzureZonesManager:
    DEFAULT_APP_ZONES_VALUE = ["Inherited"]

    def __init__(self, resource_config):
        """Init command."""
        self._resource_config = resource_config

    def get_resource_zones(self):
        """Get Availability Zones from the AzureCloudProvider Resource."""
        return [
            zone.strip() for zone in self._resource_config.availability_zones.split(",")
        ]

    def get_availability_zones(self, zones=None):
        """Get Key Vault Name for the VM-related objects."""
        if zones != self.DEFAULT_APP_ZONES_VALUE:
            return zones

        return self.get_resource_zones()
