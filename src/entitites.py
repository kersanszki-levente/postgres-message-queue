from enum import Enum, auto
from datetime import datetime

from pydantic import BaseModel

class TaskState(Enum):
    pending = auto()
    processing = auto()
    completed = auto()
    # aborted: str

class Task(BaseModel):
    id: int
    created_at: datetime
    state: TaskState
    message: str
