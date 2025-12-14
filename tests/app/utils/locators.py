from dataclasses import dataclass
from .look_up import LookBy
from .timers import TimeOut


@dataclass
class Locators:
    locator: str
    by: LookBy = LookBy.ID
    time_out: TimeOut = TimeOut.THIRTY_SECONDS
