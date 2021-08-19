import datetime
import logging

import numpy as np
import pandas as pd

from functions.interviewer_call_pattern_data_functions import (
    get_hours_worked, get_call_time_in_seconds, get_total_seconds_from_string,
    hours_on_calls, average_calls_per_hour, convert_seconds_to_datetime_format,
    respondents_interviewed, average_respondents_interviewed_per_hour, results_for_calls_with_status)
from models.error_capture import BertException
from models.interviewer_call_pattern_model import InterviewerCallPattern, InterviewerCallPatternWithNoValidData
from reports.interviewer_call_history_report import get_call_history_records

COLUMNS_TO_VALIDATE = ["call_start_time", "call_end_time", "number_of_interviews"]

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


def get_call_pattern_records_by_interviewer_and_date_range(interviewer_name, start_date_string,
                                                           end_date_string, survey_tla):
    call_history_records = get_call_history_records(
        interviewer_name, start_date_string, end_date_string, survey_tla
    )
    if not call_history_records:
        return {}

    call_history_dataframe = create_dataframe(call_history_records)
    valid_dataframe, discounted_records, discounted_fields = validate_dataframe(call_history_dataframe)

    if valid_dataframe.empty:
        return InterviewerCallPatternWithNoValidData(
            discounted_invalid_cases=f"{discounted_records[0]}, {discounted_records[1]}%",
            invalid_fields=discounted_fields
        )

    report = generate_report(valid_dataframe, len(call_history_dataframe.index), discounted_records, discounted_fields)
    return report


def create_dataframe(call_history):
    try:
        result = pd.DataFrame(data=call_history)
    except Exception as err:
        raise BertException(f"create_dataframe failed: {err}", 400)
    return result


def validate_dataframe(data):
    valid_data = data.copy()
    discounted_records = ""
    discounted_fields = ""

    valid_data.columns = valid_data.columns.str.lower()
    if invalid_data_found(valid_data):
        valid_data, discounted_records, discounted_fields = get_invalid_data(data)

    try:
        valid_data = valid_data.astype({"number_of_interviews": "int32", "dial_secs": "float64"})
        pd.to_datetime(valid_data['call_end_time'], format='%YYYY-%mm-%dd hh:mm:ss', errors='raise').notnull().all()
    except Exception as err:
        raise BertException(f"validate_dataframe failed: {err}", 400)
    return valid_data, discounted_records, discounted_fields


def invalid_data_found(data):
    timed_out_questionnaire_found = data.loc[data['status'].str.contains('Timed out', case=False)].any().any()
    missing_data_found = data.filter(COLUMNS_TO_VALIDATE).isna().any().any()

    if timed_out_questionnaire_found or missing_data_found:
        return True

    return False


def get_invalid_data(data):
    valid_records = data.copy()
    valid_records['number_of_interviews'].replace('', np.nan, inplace=True)

    valid_records.drop(valid_records.loc[valid_records['status'].str.contains(
        'Timed out', case=False)].index, inplace=True)
    valid_records.dropna(subset=COLUMNS_TO_VALIDATE, inplace=True)

    invalid_records = data[~data.index.isin(valid_records.index)]
    valid_records.reset_index(drop=True, inplace=True)
    invalid_records.reset_index(drop=True, inplace=True)

    discounted_records_total = f"{len(invalid_records.index)}/{len(data.index)}"
    discounted_records_percentage = 100 * len(invalid_records.index) / len(data.index)
    discounted_records = [discounted_records_total, round(discounted_records_percentage, 2)]

    discounted_fields = get_invalid_fields(invalid_records)

    return valid_records, discounted_records, discounted_fields


def get_invalid_fields(data):
    invalid_fields = []

    if data.loc[data['status'].str.contains('Timed out', case=False)].any().any():
        invalid_fields.append("'status' column had timed out call status")

    data = data.filter(COLUMNS_TO_VALIDATE)
    for field in data.columns[data.isna().any()]:
        invalid_fields.append(f"'{field}' column had missing data")
    return ", ".join(invalid_fields)


def generate_report(call_history_dataframe, original_number_of_records, discounted_records=None, discounted_fields=None):
    hours_worked = get_hours_worked(call_history_dataframe)
    total_call_seconds = get_call_time_in_seconds(call_history_dataframe)
    refusals_total, refusals_percentage = results_for_calls_with_status('no response', call_history_dataframe, original_number_of_records)
    successful_total, successful_percentage = results_for_calls_with_status('questionnaire|completed', call_history_dataframe, original_number_of_records)
    appointments_total, appointments_percentage = results_for_calls_with_status('appointment', call_history_dataframe, original_number_of_records)
    no_contact_total, no_contact_percentage = results_for_calls_with_status('no contact', call_history_dataframe, original_number_of_records)

    if total_call_seconds > get_total_seconds_from_string(
            hours_worked):
        raise BertException(f"Hours worked ({hours_worked}) cannot be less than time spent on calls ({datetime.timedelta(seconds=total_call_seconds)}). Please review the Call History data", 400)

    report = InterviewerCallPattern(
        hours_worked=hours_worked,
        call_time=convert_seconds_to_datetime_format(total_call_seconds),
        hours_on_calls=hours_on_calls(hours_worked, total_call_seconds),
        average_calls_per_hour=average_calls_per_hour(call_history_dataframe, hours_worked),
        respondents_interviewed=respondents_interviewed(call_history_dataframe),
        average_respondents_interviewed_per_hour=average_respondents_interviewed_per_hour(call_history_dataframe, hours_worked),
        refusals=f"{refusals_total}, {refusals_percentage}%",
        no_contacts=f"{no_contact_total}, {no_contact_percentage}%",
        answer_service="yoo-hoo",
        busy="yoo-hoo",
        disconnect="yoo-hoo",
        no_answer="yoo-hoo",
        other="yoo-hoo",
        completed_successfully=f"{successful_total}, {successful_percentage}%",
        appointments_for_contacts=f"{appointments_total}, {appointments_percentage}%",
    )

    if discounted_records is not None:
        report.discounted_invalid_cases = f"{discounted_records[0]}, {discounted_records[1]}%"
        report.invalid_fields = discounted_fields

    return report
