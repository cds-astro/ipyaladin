class WidgetCommunicationError(OSError):
    """Error raised when there is a communication error with the widget."""

    def __init__(self, message: str) -> None:
        self.message = message
        super(WidgetCommunicationError, self).__init__(message)


class WidgetReducedError(ValueError):
    """Error raised when a widget is reduced to a point when hidden."""

    def __init__(self, message: str) -> None:
        self.message = message
        super(WidgetReducedError, self).__init__(message)
