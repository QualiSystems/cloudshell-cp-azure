class BaseAzureException(Exception):
    pass


class AzureTaskTimeoutException(BaseAzureException):
    pass


class InvalidAttrException(BaseAzureException):
    pass
