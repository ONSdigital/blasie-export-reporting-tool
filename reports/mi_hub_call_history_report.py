from data_sources.cati_data import get_cati_mi_hub_call_history_from_database
from models.mi_hub_call_history_model import MiHubCallHistory


def get_mi_hub_call_history(config, questionnaire_name, questionnaire_id):
    print(f"Getting MI hub call history report data for {questionnaire_name}")
    cati_data = get_cati_mi_hub_call_history_from_database(config)
    call_history_data = []

    for item in cati_data:
        call_history_data = populate_call_history_model(
            item,
            questionnaire_id,
            questionnaire_name,
            call_history_data
        )

    return call_history_data


def populate_call_history_model(item, questionnaire_id, questionnaire_name, call_history_data):
    if item.get("InstrumentId") == questionnaire_id:
        cati_mi_hub_call_history = MiHubCallHistory(
            questionnaire_name=questionnaire_name,
            questionnaire_id=item.get("InstrumentId"),
            serial_number=item.get("PrimaryKeyValue"),
            call_number=item.get("CallNumber"),
            dial_number=item.get("DialNumber"),
            interviewer=item.get("Interviewer"),
            dial_result=item.get("DialResult"),
            dial_line_number=item.get("DialedNumber"),
            seconds_interview=item.get("dial_secs"),
            outcome_code=item.get("OutcomeCode"),
            cohort=get_cohort(item),
        )
        cati_mi_hub_call_history.generate_dial_date_and_time_fields(
            item.get("StartTime"), item.get("EndTime")
        )
        call_history_data.append(cati_mi_hub_call_history)

        return call_history_data


def get_cohort(item):
    if item.get("Cohort") is None:
        return None

    return item["Cohort"].replace("'", "")
