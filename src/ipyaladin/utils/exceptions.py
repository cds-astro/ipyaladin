class WidgetReducedError(ValueError):
    """Error raised when a widget is reduced to a point when hidden."""

    def __init__(self, message: str) -> None:
        self.message = message
        super(WidgetReducedError, self).__init__(message)


class WidgetNotReadyError(OSError):
    """Error raised when the widget is not ready."""

    def __init__(self, message: str) -> None:
        self.message = message
        super(WidgetNotReadyError, self).__init__(message)


class NameResolverWarning(UserWarning):
    """Warning raised when a name resolver is used."""

    def __init__(self, message: str) -> None:
        self.message = message
        super(NameResolverWarning, self).__init__(message)
