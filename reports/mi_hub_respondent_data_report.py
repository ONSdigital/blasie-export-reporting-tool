from data_sources.questionnaire_data import get_questionnaire_data
from models.mi_hub_respondent_data_model import MiHubRespondentData

questionnaire_fields_to_get = [
    {
        "QID.Serial_Number",
        "QHAdmin.HOut",
        "QHAdmin.Interviewer[1]",
        "Mode",
        "QDataBag.PostCode",
        "QHousehold.QHHold.Person[1].Sex",
        "QHousehold.QHHold.Person[1].tmpDoB",
        "QHousehold.QHHold.Person[1].DVAge",
        "DateTimeStamp",
        "qiD.Case_ID",
        "qiD.ShiftNo",
        "qiD.Interv",
        "notes.CaseNotes",
        "flightList.Flight1",
        "flightList.Flight2",
        "flightList.Flight3",
        "flightList.Flight4",
        "flightList.Flight5",
        "flightList.Flight6",
        "flightList.Flight7",
        "flightList.Flight8",
        "qShift.IntDate",
        "qShift.SelectionTime",
        "dmExitTime",
        "qShiftSetup.QShftDet.IntType",
        "qShift.SampInterval",
        "qShift.ShiftType",
        "qShift.Portroute",
        "qShift.Baseport",
        "qShift.Linecode",
        "qShift.FlightNum",
        "qShift.DVFlightNum",
        "qShift.PortCode",
        "qShift.PortDestination",
        "qShift.Shuttle",
        "qShift.CrossShut",
        "qShift.Vehicle",
        "qShift.IsElig",
        "qShift.FerryTime",
        "qIndiv.QNationality.Flow",
        "qAdmin.DVRespnse",
        "qAdmin.proportion",
        "qAdmin.response_visitbritain",
        "qAdmin.response_age_sex",
        "qAdmin.response_student",
        "qAdmin.response_fe_trailer",
        "qAdmin.response_migration_trailer",
        "dmTimeIsElig",
        "dmTimeAgeSex",
        "qIndiv.QNationality.UKForeign",
        "qIndiv.QBStudent.StudyCheck",
        "qIndiv.QExpend.DVExpend",
        "qIndiv.QAgeSex.Age",
        "qIndiv.QAgeSex.Sex"
    }
]


def get_mi_hub_respondent_data(config, questionnaire_name):
    print(f"Getting MI hub respondent data report data for {questionnaire_name}")
    mi_hub_respondent_data_list = []
    questionnaire_data = get_questionnaire_data(
        questionnaire_name, config, questionnaire_fields_to_get
    )
    for item in questionnaire_data:
        mi_hub_respondent_data_record = MiHubRespondentData(
            serial_number=item.get("qiD.Serial_Number"),
            outcome_code=item.get("qhAdmin.HOut"),
            date_completed=item.get("dateTimeStamp"),
            interviewer=item.get("qhAdmin.Interviewer[1]"),
            mode=item.get("mode"),
            postcode=item.get("qDataBag.PostCode"),
            gender=item.get("qHousehold.QHHold.Person[1].Sex"),
            date_of_birth=item.get("qHousehold.QHHold.Person[1].tmpDoB"),
            age=item.get("qHousehold.QHHold.Person[1].DVAge"),
            Case_ID=item.get("qiD.Case_ID"),
            ShiftNo=item.get("qiD.ShiftNo"),
            Interv=item.get("qiD.Interv"),
            CaseNotes=item.get("notes.CaseNotes"),
            Flight1=item.get("flightList.Flight1"),
            Flight2=item.get("flightList.Flight2"),
            Flight3=item.get("flightList.Flight3"),
            Flight4=item.get("flightList.Flight4"),
            Flight5=item.get("flightList.Flight5"),
            Flight6=item.get("flightList.Flight6"),
            Flight7=item.get("flightList.Flight7"),
            Flight8=item.get("flightList.Flight8"),
            IntDate=item.get("qShift.IntDate"),
            SelectionTime=item.get("qShift.SelectionTime"),
            DMExitTime=item.get("dmExitTime"),
            IntType=item.get("qShiftSetup.QShftDet.IntType"),
            SampInterval=item.get("qShift.SampInterval"),
            ShiftType=item.get("qShift.ShiftType"),
            Portroute=item.get("qShift.Portroute"),
            Baseport=item.get("qShift.Baseport"),
            Linecode=item.get("qShift.Linecode"),
            FlightNum=item.get("qShift.FlightNum"),
            DVFlightNum=item.get("qShift.DVFlightNum"),
            PortCode=item.get("qShift.PortCode"),
            PortDestination=item.get("qShift.PortDestination"),
            Shuttle=item.get("qShift.Shuttle"),
            CrossShut=item.get("qShift.CrossShut"),
            Vehicle=item.get("qShift.Vehicle"),
            IsElig=item.get("qShift.IsElig"),
            FerryTime=item.get("qShift.FerryTime"),
            Flow=item.get("qIndiv.QNationality.Flow"),
            DVRespnse=item.get("qAdmin.DVRespnse"),
            proportion=item.get("qAdmin.proportion"),
            response_visitbritain=item.get("qAdmin.response_visitbritain"),
            response_age_sex=item.get("qAdmin.response_age_sex"),
            response_student=item.get("qAdmin.response_student"),
            response_fe_trailer=item.get("qAdmin.response_fe_trailer"),
            response_migration_trailer=item.get("qAdmin.response_migration_trailer"),
            DMTimeIsElig=item.get("dmTimeIsElig"),
            DMTimeAgeSex=item.get("dmTimeAgeSex"),
            UKForeign=item.get("qIndiv.QNationality.UKForeign"),
            StudyCheck=item.get("qIndiv.QBStudent.StudyCheck"),
            Expenditure=item.get("qIndiv.QExpend.DVExpend"),
            Age=item.get("qIndiv.QAgeSex.Age"),
            Sex=item.get("qIndiv.QAgeSex.Sex")
        )
        if not all(
            value in ("", None)
            for value in vars(mi_hub_respondent_data_record).values()
        ):
            mi_hub_respondent_data_list.append(mi_hub_respondent_data_record)
    return mi_hub_respondent_data_list
