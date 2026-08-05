

class NotFound(Exception):
    """Exception raised when a requested resource is not found."""
    pass


class BankUnavailable(Exception):
    """Exception raised when the bank service is unavailable."""
    pass