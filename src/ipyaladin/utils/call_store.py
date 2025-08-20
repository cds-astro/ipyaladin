from traitlets import (
    Any,
)


class CallStore:
    """A simple call store.

    This is used to store user calls to Aladin API in case the widget is not properly
    loaded on the JS side. Whenever it gets loaded, then the calls are run in the
    inserting order.
    """

    def __init__(self) -> None:
        self.calls = []

    def add(self, func: Any, *args: Any, **kwargs: Any) -> None:
        """Add a call to the store."""
        self.calls.append((func, args, kwargs))

    def run_all(self) -> None:
        """Run all the stored calls in the right order."""
        for func, args, kwargs in self.calls:
            func(*args, **kwargs)
