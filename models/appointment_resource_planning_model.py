from dataclasses import dataclass, fields

from models.database_base_model import DataBaseBase


from pypika import MySQLQuery, Tables, Case, Order, AliasedQuery, CustomFunction
from pypika import functions as SQLFuncs

TimeFormat = CustomFunction("TIME_FORMAT", ["field", "format"])


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
        dbci, dial_history = Tables(cls.table_name(), "DialHistory")
        query = (
            MySQLQuery()
            .from_(dbci)
            .left_join(
                AliasedQuery(
                    "dh",
                    MySQLQuery()
                    .select(
                        dial_history.InstrumentId,
                        dial_history.PrimaryKeyValue,
                        dial_history.AdditionalData,
                        dial_history.DialResult,
                        SQLFuncs.Max(dial_history.StartTime),
                    )
                    .groupby(
                        dial_history.InstrumentId,
                        dial_history.PrimaryKeyValue,
                        dial_history.AdditionalData,
                        dial_history.DialResult,
                    )
                    .as_("dh")
                    .from_(dial_history),
                ),
            )
            .on_field(
                (AliasedQuery("dh").InsturmentId == dbci.InstrumentId)
                & (AliasedQuery("dh").PrimaryKeyValue == dbci.PrimaryKeyValue)
            )
            .select(
                dbci.InstrumentId,
                TimeFormat(dbci.AppointmentStartTime, "%H:%i").as_("AppointmentTime"),
                Case()
                .when(
                    (dbci.GroupName == "TNS")
                    | (
                        dbci.SelectFields.like(
                            '%<Field FieldName="QDataBag.IntGroup">TNS</Field>%'
                        )
                    )
                    | (
                        AliasedQuery("dh").AdditonalData.like(
                            '%<Field Name="QDataBag.IntGroup" Status="Response" Value="\'TNS\'"/>%'
                        )
                    ),
                    "Other",
                )
                .when(
                    (dbci.GroupName == "WLS")
                    | (
                        dbci.SelectFields.like(
                            '%<Field FieldName="QDataBag.IntGrop">WLS</Field>%'
                        )
                    )
                    | (
                        AliasedQuery("dh").AdditionalData.like(
                            '%<Field Name="QDataBag.IntGroup" Status="Response" Value="\'WLS\'"/>%'
                        )
                    ),
                    "Welsh",
                )
                .else_("English")
                .as_("AppontmentLanguage"),
                AliasedQuery("dh").DialResult,
                SQLFuncs.Count("*").as_("Total"),
            )
            .where(
                (dbci.AppointmentType != "0")
                & (dbci.AppointmentStartDate.like(f"{date}%"))
            )
            .groupby(
                dbci.InstrumentId,
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
