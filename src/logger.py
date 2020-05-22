from typing import List, Callable
from dataclasses import dataclass
from datetime import datetime
import functools


@dataclass
class _LogMessage:
    """
    Holds info on a log message for better searching.
    """
    date: datetime
    name: str
    level: str
    message: str

    def __str__(self) -> str:
        date_string = self.date.strftime("%H:%M:%S")
        return f'{date_string} {self.name} [{self.level}]: "{self.message}"'


LOGS: List[_LogMessage] = []


class Logger:
    """
    A logger, one per file.
    """
    def __init__(self, name: str) -> None:
        self.name = name

        self.DEBUG = self._construct_log_function("DEBUG")
        self.INFO = self._construct_log_function("INFO")
        self.WARNING = self._construct_log_function("WARNING")
        self.ERROR = self._construct_log_function("ERROR")
        self.USER_ERROR = self._construct_log_function("USER_ERROR")

    def _log(self, level: str, msg: str) -> None:
        """
        Log a msg using the given level.
        """
        log_message = _LogMessage(datetime.today(), self.name, level, msg)
        LOGS.append(log_message)

        print(log_message)
        with open("bot.log", "a+") as log_file:
            log_file.write(str(log_message) + "\n")

    def _construct_log_function(self, level: str) -> Callable[[str], None]:
        """
        Return a functon to log a msg with a pre defined level.
        """
        return functools.partial(self._log, level)
