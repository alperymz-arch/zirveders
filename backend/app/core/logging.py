import logging
import sys


def setup_logging(env: str = "development") -> None:
    level = logging.INFO if env == "production" else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )
