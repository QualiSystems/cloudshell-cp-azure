class BaseAzureException(Exception):
    pass


class AzureTaskTimeoutException(BaseAzureException):
    pass


class InvalidAttrException(BaseAzureException):
    pass


class ResourceNotFoundException(BaseAzureException):
    pass


class MultipleResourceFoundException(BaseAzureException):
    pass


class NetworkNotFoundException(BaseAzureException):
    pass
