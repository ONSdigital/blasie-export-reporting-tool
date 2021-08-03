import pytest

from interviewer_call_pattern_report.report import *
from models.interviewer_call_pattern import InterviewerCallPattern
from models.error_capture import BertException


def test_get_call_pattern_records_by_interviewer_and_date_range_returns_error():
    with pytest.raises(BertException) as error:
        get_call_pattern_records_by_interviewer_and_date_range("ricer", "blah", "blah")

    assert error.value.message == "Invalid date range parameters provided"
    assert error.value.code == 400


def test_generate_report(call_history_dataframe):
    assert generate_report(call_history_dataframe) == InterviewerCallPattern(
        hours_worked='2:27:57',
        call_time='0:02:45',
        hours_on_calls_percentage='1.86%',
        average_calls_per_hour=3.24,
        respondents_interviewed=8,
        households_completed_successfully=1,
        average_respondents_interviewed_per_hour=3.24,
        no_contacts_percentage='50.0%',
        appointments_for_contacts_percentage='0.0%'
    )


@pytest.mark.parametrize(
    "column_names",
    [
        (["call_start_time"]),
        (["call_end_time"]),
        (["number_of_interviews"]),
        (["call_start_time", "call_end_time"]),
        (["call_start_time", "call_end_time", "number_of_interviews"]),
    ],
)
def test_add_invalid_fields_to_report(column_names, interviewer_call_pattern_report, invalid_call_history_dataframe, call_history_dataframe):

    for col in column_names:
        invalid_call_history_dataframe.loc[
            invalid_call_history_dataframe['questionnaire_id'] == "05cf69af-1a4e-47df-819a-928350fdda5a", col] = np.nan

    add_invalid_fields_to_report(
        interviewer_call_pattern_report,
        invalid_call_history_dataframe,
        call_history_dataframe
    )

    assert interviewer_call_pattern_report.invalid_fields == ", ".join(column_names)


def test_generate_report_returns_error(call_history_dataframe):
    call_history_dataframe.loc[call_history_dataframe['questionnaire_id'] == '05cf69af-3a4e-47df-819a-928350fdda5a', [
        'call_start_time']] = 'blah'

    with pytest.raises(BertException) as error:
        generate_report(call_history_dataframe)
    assert error.value.message == "generate_report failed: Can only use .dt accessor with datetimelike values"
    assert error.value.code == 400


def test_validate_dataframe_with_no_invalid_data(call_history_dataframe):
    valid_dataframe, invalid_dataframe = validate_dataframe(call_history_dataframe)
    assert valid_dataframe.columns.to_series().str.islower().all()
    assert type(valid_dataframe) == pd.DataFrame
    assert len(invalid_dataframe.index) == 0


def test_validate_dataframe_with_invalid_data(call_history_dataframe):
    call_history_dataframe.loc[
        call_history_dataframe["questionnaire_id"] == "05cf69af-3a4e-47df-819a-928350fdda5a", "call_end_time"] = np.nan

    valid_dataframe, invalid_dataframe = validate_dataframe(call_history_dataframe)
    assert valid_dataframe.columns.to_series().str.islower().all()
    assert type(valid_dataframe) == pd.DataFrame
    assert len(invalid_dataframe.index) == 2


def test_validate_dataframe_returns_error(call_history_dataframe):
    call_history_dataframe.loc[
        call_history_dataframe[
            "questionnaire_id"] == "05cf69af-3a4e-47df-819a-928350fdda5a", "number_of_interviews"] = "hey-yo!"

    with pytest.raises(BertException) as error:
        validate_dataframe(call_history_dataframe)
    assert error.value.message == "validate_dataframe failed: invalid literal for int() with base 10: \'hey-yo!\'"
    assert error.value.code == 400


def test_drop_and_return_invalidated_records(call_history_dataframe):
    actual_valid_records, actual_invalid_records = drop_and_return_invalidated_records(call_history_dataframe)
    assert len(actual_valid_records.index) == 8
    assert len(actual_invalid_records.index) == 0


@pytest.mark.parametrize(
    "column_names",
    [
        (["call_start_time"]),
        (["call_end_time"]),
        (["number_of_interviews"]),
        (["call_start_time", "call_end_time"]),
        (["call_start_time", "call_end_time", "number_of_interviews"]),
    ],
)
def test_get_invalid_fields(column_names, call_history_dataframe):
    for col in column_names:
        call_history_dataframe.loc[
            call_history_dataframe['questionnaire_id'] == "05cf69af-3a4e-47df-819a-928350fdda5a", col] = np.nan
    assert get_invalid_fields(call_history_dataframe) == ", ".join(column_names)
