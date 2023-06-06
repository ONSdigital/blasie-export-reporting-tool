from dataclasses import dataclass, fields
from datetime import datetime
from typing import Optional, Union

from models.database_base_model import DatabaseBase


class CallHistoryReport:
    def __init__(self, cati_data):
        self.cati_data = cati_data
        self.data = []

    def populate(self, questionnaire_id, questionnaire_name):
        for item in self.cati_data:
            self.populate_call_history_model(item, questionnaire_id, questionnaire_name)

    def populate_call_history_model(self, item, questionnaire_id, questionnaire_name):
        if item.get("InstrumentId") == questionnaire_id:
            cati_mi_hub_call_history = MiHubCallHistory(
                questionnaire_name=questionnaire_name,
                questionnaire_id=item.get("InstrumentId"),
                serial_number=item.get("PrimaryKeyValue"),
                dial_date=self.get_dial_date(item),
                dial_time=self.get_dial_time(item),
                end_time=self.get_end_time(item),
                call_number=item.get("CallNumber"),
                dial_number=item.get("DialNumber"),
                interviewer=item.get("Interviewer"),
                dial_result=item.get("DialResult"),
                dial_line_number=item.get("DialedNumber"),
                seconds_interview=item.get("dial_secs"),
                outcome_code=item.get("OutcomeCode"),
                cohort=self.get_cohort(item),
            )
            self.data.append(cati_mi_hub_call_history)

    @staticmethod
    def get_dial_date(item):
        return item.get("StartTime").strftime("%Y%m%d")

    @staticmethod
    def get_dial_time(item):
        return item.get("StartTime").strftime("%H:%M:%S")

    @staticmethod
    def get_end_time(item):
        if item.get("EndTime") is not None:
            return item.get("EndTime").strftime("%H:%M:%S")

    @staticmethod
    def get_cohort(item):
        if item.get("Cohort") is None:
            return None

        return item["Cohort"].replace("'", "")


@dataclass
class MiHubCallHistory:
    questionnaire_name: str = ""
    questionnaire_id: Optional[str] = None
    serial_number: Optional[str] = None
    dial_date: str = ""
    dial_time: str = ""
    end_time: str = ""
    seconds_interview: Optional[int] = None
    call_number: Optional[int] = None
    dial_number: Optional[int] = None
    interviewer: Optional[str] = None
    dial_result: Optional[int] = None
    dial_line_number: Optional[int] = None
    appointment_type: str = ""
    outcome_code: Union[int, str] = ""
    cohort: str = ""

    @classmethod
    def fields(cls):
        return [field.name for field in fields(cls)]


@dataclass
class CatiMiHubCallHistoryTable(DatabaseBase):
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

    @staticmethod
    def get_outcome_code():
        return """ExtractValue(`AdditionalData`, '/Fields/Field[@Name="QHAdmin.HOut"]/@Value') AS OutcomeCode"""

    @staticmethod
    def get_cohort():
        return """ExtractValue(`AdditionalData`, '/Fields/Field[@Name="qDataBag.Cohort"]/@Value') AS Cohort"""

    @classmethod
    def table_name(cls):
        return "cati.DialHistory"

    @classmethod
    def extra_fields(cls):
        return [
            "ABS(TIME_TO_SEC(TIMEDIFF(EndTime, StartTime))) as dial_secs",
            cls.get_outcome_code(),
            cls.get_cohort(),
        ]
