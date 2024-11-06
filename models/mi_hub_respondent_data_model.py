from dataclasses import dataclass, fields
from typing import Optional
from datetime import datetime


@dataclass
class MiHubRespondentData:
    postcode: str
    mode: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    age: Optional[int] = None
    serial_number: str
    outcome_code: str
    date_completed: str
    interviewer: str

    @classmethod
    def fields(cls):
        return [field.name for field in fields(cls)]
