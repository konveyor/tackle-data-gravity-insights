import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(show_path=False)]
)


class Log(object):
    log = logging.getLogger("rich")

    @staticmethod
    def info(msg: str):
        Log.log.info(msg, extra={"markup": True})

    @staticmethod
    def warn(msg: str):
        Log.log.warn(msg, extra={"markup": True})

    @staticmethod
    def debug(msg: str):
        Log.log.debug(msg, extra={"markup": True})

    @staticmethod
    def error(msg: str):
        Log.log.error(msg, extra={"markup": True})
