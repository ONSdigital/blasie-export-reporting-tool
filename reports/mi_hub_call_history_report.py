from data_sources.cati_data import get_cati_mi_hub_call_history_from_database
from models.mi_hub_call_history_model import MiHubCallHistoryReport


def get_mi_hub_call_history(config, questionnaire_name, questionnaire_id):
    print(f"Getting MI hub call history report data for {questionnaire_name}")
    call_history_report = MiHubCallHistoryReport(
        get_cati_mi_hub_call_history_from_database(config))

    call_history_report.populate(questionnaire_id, questionnaire_name)

    return call_history_report.data
