import logging

import flask

from data_sources.cati_data import get_cati_mi_hub_call_history_from_database
from functions.google_storage_functions import init_google_storage
from models.config_model import Config
from reports.mi_hub_call_history_report import get_mi_hub_call_history
from reports.mi_hub_respondent_data_report import get_mi_hub_respondent_data
from services.deliver_mi_hub_reports_service import DeliverMiHubReportsService


def deliver_mi_hub_reports_cloud_function_processor(
        request: flask.Request, config: Config, get_cati_mi_hub_call_history
) -> str:
    request_json = get_json_request(request)
    google_storage = init_storage_bucket(config)

    return get_call_history_data(
        request_json,
        create_mi_hub_get_call_history(get_cati_mi_hub_call_history),
        create_get_respondent_data_with_config(config),
        create_upload_mi_hub_report(google_storage)
    )


def get_json_request(request):
    request_json = request.get_json()
    if request_json is None:
        logging.error(
            "deliver_mi_hub_reports_cloud_function_processor was not triggered due to an invalid request"
        )
        raise Exception(
            "deliver_mi_hub_reports_cloud_function_processor was not triggered due to an invalid request"
        )
    return request_json


def init_storage_bucket(config):
    google_storage = init_google_storage(config)
    if google_storage.bucket is None:
        logging.error(
            f"Connection to storage bucket {config.nifi_staging_bucket} failed"
        )
        raise Exception(
            f"Connection to storage bucket {config.nifi_staging_bucket} failed", 500
        )
    return google_storage


def get_call_history_data(request_json, get_call_history, get_respondent_data, upload_reports_to_gcp):
    questionnaire_name = request_json["name"]
    questionnaire_id = request_json["id"]

    mi_hub_call_history = get_call_history(questionnaire_name, questionnaire_id)
    mi_hub_respondent_data = get_respondent_data(questionnaire_name)

    return upload_reports_to_gcp(questionnaire_name, mi_hub_call_history, mi_hub_respondent_data)


def create_mi_hub_get_call_history(get_cati_mi_hub_call_history):
    def get_call_history(questionnaire_name, questionnaire_id):
        return get_mi_hub_call_history(questionnaire_name,
                                       questionnaire_id,
                                       get_cati_mi_hub_call_history)

    return get_call_history


def create_get_respondent_data_with_config(config):
    def get_respondent_data(questionnaire_name):
        return get_mi_hub_respondent_data(config, questionnaire_name)

    return get_respondent_data


def create_upload_mi_hub_report(google_storage):
    def upload_mi_hub_reports(questionnaire_name, mi_hub_call_history,
                              mi_hub_respondent_data):
        return DeliverMiHubReportsService.upload_mi_hub_reports_to_gcp(
            questionnaire_name, mi_hub_call_history, mi_hub_respondent_data, google_storage)

    return upload_mi_hub_reports
