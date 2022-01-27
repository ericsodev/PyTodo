from __future__ import annotations

from enum import Enum
from typing import List
import datetime


class Categories(Enum):
    def __init__(self):
        pass


class Todo:
    """ A class representing a task

    """
    date: datetime.date
    name: str
    type = List[Categories]

    def __init__(self) -> None:
        pass


