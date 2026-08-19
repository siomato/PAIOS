from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CommandType(str, Enum):
    OPEN = "open"
    OBSERVE = "observe"
    READ = "read"
    FIND = "find"
    CLICK = "click"
    SEARCH = "search"
    FILL = "fill"
    PRESS = "press"
    WAIT = "wait"


class PAIOSCommand(BaseModel):
    command: CommandType

    url: Optional[str] = None
    target: Optional[str] = None
    query: Optional[str] = None
    text: Optional[str] = None
    key: Optional[str] = None
    seconds: Optional[float] = None