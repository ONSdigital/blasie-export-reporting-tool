from dataclasses import dataclass, fields
from datetime import datetime
from models.db_base import DBBase


@dataclass
class MICallHistory:
    questionnaire_id: str
    serial_number: str
    internal_key: int
    call_number: int
    dial_number: int
    interviewer: str
    dial_result: int
    dial_line_number: int
    seconds_dial: int
    end_time: str = ""
    questionnaire_name: str = ""
    dial_date: str = ""
    dial_time: str = ""
    entry_priority: int = ""
    exit_priority: int = ""
    appointment_type: str = ""
    seconds_interview: datetime = ""
    outcome_code: int = ""

    def generate_dial_date_and_time_fields(self, start_datetime, end_datetime):
        self.dial_date = start_datetime.strftime("%Y%m%d")
        self.dial_time = start_datetime.strftime("%H:%M:%S")
        if end_datetime is not None:
            self.end_time = end_datetime.strftime("%H:%M:%S")
        pass


@dataclass
class CatiMiCallHistoryTable(DBBase):
    InstrumentId: str
    PrimaryKeyValue: str
    Id: int
    StartTime: datetime
    CallNumber: int
    DialNumber: int
    Interviewer: str
    DialResult: str
    DialedNumber: str
    AppointmentInfo: str
    EndTime: datetime

    @classmethod
    def table_name(cls):
        return "cati.DialHistory"

    @classmethod
    def extra_fields(cls):
        return ["ABS(TIME_TO_SEC(TIMEDIFF(EndTime, StartTime))) as dialsecs"]
