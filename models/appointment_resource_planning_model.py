from dataclasses import dataclass, fields


from models.database_base_model import DataBaseBase

from pypika import Query, Tables, Function, Case, Order, AliasedQuery

from pypika import functions as SQLFuncs

# TimeFormat = CustomFunction("TIME_FORMAT", ["field", "format"])
class TimeFormat(Function):
    def __init__(self, field, format, alias=None):
        print(f"TIMEFORMAT {field} {format}")
        super(TimeFormat, self).__init__("TIME_FORMAT", field, format, alias=alias)


@dataclass
class AppointmentResourcePlanning:
    questionnaire_name: str = ""
    appointment_time: str = ""
    appointment_language: str = ""
    dial_result: str = ""
    total: int = None

    @classmethod
    def fields(cls):
        return [field.name for field in fields(cls)]


@dataclass
class CatiAppointmentResourcePlanningTable(DataBaseBase):
    InstrumentId: str
    AppointmentStartDate: str
    AppointmentStartTime: str
    GroupName: str
    DialResult: str
    AppointmentType: int

    @classmethod
    def get_appointments_for_date(cls, config, date):
        dhci, dial_history = Tables(cls.table_name(), "DialHistory")
        query = (
            Query()
            .from_(dhci)
            .left_join(
                AliasedQuery(
                    "dh",
                    Query()
                    .select(
                        dial_history.InstrumentId,
                        dial_history.PrimaryKeyValue,
                        dial_history.AdditionalData,
                        dial_history.DialResult,
                        SQLFuncs.Max(dial_history.StartTime),
                    )
                    .from_(dial_history),
                ),
            )
            .on_field(
                dial_history.InsturmentId == dhci.InstrumentId
                and dial_history.PrimaryKeyValue == dhci.PrimaryKeyValue
            )
            .select(
                dhci.InstrumentId,
                TimeFormat(dhci.AppointmentStartTime, "%H:%%i").as_("AppointmentTime"),
                Case()
                .when(
                    dhci.GroupName == "TNS"
                    or dhci.SelectFields.like(
                        '%<Field FieldName="QDataBag.IntGroup">TNS</Field>%'
                    )
                    or AliasedQuery("dh").AdditonalData.like(
                        """%<Field Name="QDataBag.IntGroup" Status="Response" Value="\\'TNS\\'"/>%"""
                    ),
                    "Other",
                )
                .when(
                    dhci.GroupName == "WLS"
                    or dhci.SelectFields.like(
                        '%<Field FieldName="QDataBag.IntGrop">WLS</Field>%'
                    )
                    or AliasedQuery("dh").AdditionalData.like(
                        """%<Field Name="QDataBag.IntGroup" Status="Response" Value="\\'WLS\\'"/>%"""
                    ),
                    "Welsh",
                )
                .else_("English")
                .as_("AppontmentLanguage"),
                AliasedQuery("dh").DialResult,
                SQLFuncs.Count("*").as_("Total"),
            )
            .where(
                dhci.AppointmentType != "0"
                and dhci.AppointmentStartDate.like(f"{date}%")
            )
            .groupby(
                dhci.InstrumentId,
                "AppointmentTime",
                "AppointmentLanguage",
                dial_history.DialResult,
            )
            .orderby("AppointmentTime", order=Order.asc)
            .orderby("AppointmentLanguage", order=Order.asc)
        )

        return cls.query(config, str(query))

    @classmethod
    def table_name(cls):
        return "cati.DaybatchCaseInfo"
