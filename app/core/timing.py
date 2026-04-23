from time import perf_counter


class Timer:
    """Small helper to report endpoint/service latency in milliseconds."""

    def __init__(self) -> None:
        self._start = perf_counter()

    @property
    def elapsed_ms(self) -> int:
        return round((perf_counter() - self._start) * 1000)

