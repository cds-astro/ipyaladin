class WidgetCommunicationError(OSError):
    """Error raised when there is a communication error with the widget."""

    def __init__(self, message: str) -> None:
        self.message = message
        super(WidgetCommunicationError, self).__init__(message)


class NameResolverWarning(UserWarning):
    """Warning raised when a name resolver is used."""

    def __init__(self, message: str) -> None:
        self.message = message
        super(NameResolverWarning, self).__init__(message)
