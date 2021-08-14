from dataclasses import dataclass, fields

from pypika import MySQLQuery, Tables, Case, Order, AliasedQuery, CustomFunction
from pypika import functions as SQLFuncs

from models.database_base_model import DataBaseBase

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
        dci, dh = Tables("DaybatchCaseInfo", "DialHistory")
        query = (
            MySQLQuery()
                .from_(dci)
                .left_join(
                AliasedQuery(
                    "dh",
                    MySQLQuery()
                        .select(
                        dh.InstrumentId,
                        dh.PrimaryKeyValue,
                        dh.AdditionalData,
                        dh.DialResult,
                        SQLFuncs.Max(dh.StartTime),
                    )
                        .groupby(
                        dh.InstrumentId,
                        dh.PrimaryKeyValue,
                        dh.AdditionalData,
                        dh.DialResult,
                    )
                        .as_("dh")
                        .from_(dh),
                ),
            )
                .on_field(
                (AliasedQuery("dh").InsturmentId == dci.InstrumentId)
                & (AliasedQuery("dh").PrimaryKeyValue == dci.PrimaryKeyValue)
            )
                .select(
                dci.InstrumentId,
                TimeFormat(dci.AppointmentStartTime, "%H:%i").as_("AppointmentTime"),
                Case()
                    .when(
                    (dci.GroupName == "TNS")
                    | (
                        dci.SelectFields.like(
                            '%<Field FieldName="QDataBag.IntGroup">TNS</Field>%'
                        )
                    )
                    | (
                        AliasedQuery("dh").AdditionalData.like(
                            '%<Field Name="QDataBag.IntGroup" Status="Response" Value="\'TNS\'"/>%'
                        )
                    ),
                    "Other",
                )
                    .when(
                    (dci.GroupName == "WLS")
                    | (
                        dci.SelectFields.like(
                            '%<Field FieldName="QDataBag.IntGroup">WLS</Field>%'
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
                (dci.AppointmentType != "0")
                & (dci.AppointmentStartDate.like(f"{date}%"))
            )
                .groupby(
                dci.InstrumentId,
                "AppointmentTime",
                "AppointmentLanguage",
                dh.DialResult,
            )
                .orderby("AppointmentTime", order=Order.asc)
                .orderby("AppointmentLanguage", order=Order.asc)
        )

        return cls.query(config, str(query))

    @classmethod
    def table_name(cls):
        return "cati.DaybatchCaseInfo"
