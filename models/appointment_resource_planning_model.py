from dataclasses import dataclass, fields

from pypika import (
    MySQLQuery,
    Tables,
    Case,
    Order,
    AliasedQuery,
    CustomFunction,
    Criterion,
)
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
        daybatch_case_info, dial_history = Tables("DaybatchCaseInfo", "DialHistory")
        query = (
            MySQLQuery()
            .from_(daybatch_case_info)
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
            .on(
                Criterion.all(
                    [
                        AliasedQuery("dh").InstrumentId
                        == daybatch_case_info.InstrumentId,
                        AliasedQuery("dh").PrimaryKeyValue
                        == daybatch_case_info.PrimaryKeyValue,
                    ]
                )
            )
            .select(
                daybatch_case_info.InstrumentId,
                TimeFormat(daybatch_case_info.AppointmentStartTime, "%H:%i").as_(
                    "AppointmentTime"
                ),
                Case()
                .when(
                    Criterion.any(
                        [
                            daybatch_case_info.GroupName == "TNS",
                            daybatch_case_info.SelectFields.like(
                                '%<Field FieldName="QDataBag.IntGroup">TNS</Field>%'
                            ),
                            AliasedQuery("dh").AdditionalData.like(
                                '%<Field Name="QDataBag.IntGroup" Status="Response" Value="\'TNS\'"/>%'
                            ),
                        ]
                    ),
                    "Other",
                )
                .when(
                    Criterion.any(
                        [
                            daybatch_case_info.GroupName == "WLS",
                            daybatch_case_info.SelectFields.like(
                                '%<Field FieldName="QDataBag.IntGroup">WLS</Field>%'
                            ),
                            AliasedQuery("dh").AdditionalData.like(
                                '%<Field Name="QDataBag.IntGroup" Status="Response" Value="\'WLS\'"/>%'
                            ),
                        ]
                    ),
                    "Welsh",
                )
                .else_("English")
                .as_("AppontmentLanguage"),
                AliasedQuery("dh").DialResult,
                SQLFuncs.Count("*").as_("Total"),
            )
            .where(
                (daybatch_case_info.AppointmentType != "0")
                & (daybatch_case_info.AppointmentStartDate.like(f"{date}%"))
            )
            .groupby(
                daybatch_case_info.InstrumentId,
                AliasedQuery("AppointmentTime"),
                AliasedQuery("AppointmentLanguage"),
                dial_history.DialResult,
            )
            .orderby(AliasedQuery("AppointmentTime"), order=Order.asc)
            .orderby(AliasedQuery("AppointmentLanguage"), order=Order.asc)
        )

        return cls.query(config, str(query))

    @classmethod
    def table_name(cls):
        return "cati.DaybatchCaseInfo"
