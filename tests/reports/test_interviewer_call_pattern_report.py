import pytest

import numpy as np
import pandas as pd

from pandas.testing import assert_frame_equal

from models.interviewer_call_pattern_model import InterviewerCallPattern, InterviewerCallPatternWithNoValidData
from models.error_capture import BertException
from reports.interviewer_call_pattern_report import (
    invalid_data_found, generate_report,
    get_call_pattern_records_by_interviewer_and_date_range,
    validate_dataframe, handle_no_contacts_breakdown
)


def test_get_call_pattern_report_when_data_is_completely_invalid(call_history_records, mocker):
    mock_interviewer_name = 'el4president'
    mock_date = '2022-01-24'
    mock_discounted_invalid_records = ["100", 100]
    mock_invalid_fields = "aaaaaaaallll the fields"

    mocker.patch("reports.interviewer_call_pattern_report.get_call_history_records",
                 return_value=call_history_records)
    mocker.patch("reports.interviewer_call_pattern_report.validate_dataframe",
                 return_value=(pd.DataFrame(), mock_discounted_invalid_records, mock_invalid_fields))

    x = get_call_pattern_records_by_interviewer_and_date_range(
        mock_interviewer_name, mock_date, mock_date, None)

    assert x == InterviewerCallPatternWithNoValidData(
        discounted_invalid_cases=f"{mock_discounted_invalid_records[0]}, {mock_discounted_invalid_records[1]}%",
        invalid_fields=mock_invalid_fields
    )


def test_get_call_pattern_records_by_interviewer_and_date_range_returns_error():
    with pytest.raises(BertException) as error:
        get_call_pattern_records_by_interviewer_and_date_range("ricer", "blah", "blah", None)
    assert error.value.message == "Invalid date range parameters provided"
    assert error.value.code == 400


def test_validate_dataframe_drops_invalid_data_and_returns_information(missing_dataframe):
    dataframe, discounted_records, discounted_fields = validate_dataframe(missing_dataframe)
    assert len(dataframe.index) == 2
    assert discounted_records == ["1/3", 33.33]
    assert discounted_fields == "'call_end_time' column had missing data"


def test_validate_dataframe_returns_valid_dataframe_with_lower_case_column_names(valid_dataframe):
    dataframe, discounted_records, discounted_fields = validate_dataframe(valid_dataframe)
    assert all(i.islower() for i in list(dataframe.columns))


def test_validate_dataframe_returns_valid_dataframe_with_no_discounted_records_or_fields(valid_dataframe):
    dataframe, discounted_records, discounted_fields = validate_dataframe(valid_dataframe)
    assert_frame_equal(left=dataframe, right=valid_dataframe, check_dtype=False)
    assert discounted_records == ""
    assert discounted_fields == ""


def test_validate_dataframe_returns_has_converted_necessary_columns_to_the_correct_types(valid_dataframe):
    dataframe, discounted_records, discounted_fields = validate_dataframe(valid_dataframe)
    assert dataframe['number_of_interviews'].dtype == np.int32
    assert dataframe['dial_secs'].dtype == np.float64
    assert str(dataframe['call_start_time'].dtype) == 'datetime64[ns, UTC]'
    assert str(dataframe['call_end_time'].dtype) == 'datetime64[ns, UTC]'


def test_validate_dataframe_raises_error(dodgy_date_value_dataframe):
    with pytest.raises(BertException) as error:
        validate_dataframe(dodgy_date_value_dataframe)
    assert error.value.message == "validate_dataframe failed: time data 'SURPRISE!!!!' does not match format '%YYYY-%mm-%dd hh:mm:ss' (match)"
    assert error.value.code == 400


def test_invalid_data_found_returns_false(valid_dataframe):
    assert invalid_data_found(valid_dataframe) is False


def test_invalid_data_found_returns_true(missing_dataframe):
    assert invalid_data_found(missing_dataframe) is True


def test_generate_report_returns_report_with_no_invalid_records(valid_dataframe):
    assert generate_report(valid_dataframe, 10) == InterviewerCallPattern(
        hours_worked='0:48:05',
        call_time='0:12:50',
        hours_on_calls='26.69%',
        average_calls_per_hour=12.48,
        respondents_interviewed=10,
        average_respondents_interviewed_per_hour=12.48,
        refusals='0/10, 0.0%',
        no_contacts='0/10, 0.0%',
        completed_successfully='2/10, 20.0%',
        appointments_for_contacts='6/10, 60.0%',
        no_contact_answer_service='n/a',
        no_contact_busy='n/a',
        no_contact_disconnect='n/a',
        no_contact_no_answer='n/a',
        no_contact_other='n/a',
        discounted_invalid_cases='0',
        invalid_fields='n/a')


def test_generate_report_returns_report_with_invalid_records(valid_dataframe):
    assert generate_report(valid_dataframe, 10, ["1/10", 1], "'call_end_time' column had missing data") == InterviewerCallPattern(
        hours_worked='0:48:05',
        call_time='0:12:50',
        hours_on_calls='26.69%',
        average_calls_per_hour=12.48,
        respondents_interviewed=10,
        average_respondents_interviewed_per_hour=12.48,
        refusals='0/10, 0.0%',
        no_contacts='0/10, 0.0%',
        completed_successfully='2/10, 20.0%',
        appointments_for_contacts='6/10, 60.0%',
        no_contact_answer_service='n/a',
        no_contact_busy='n/a',
        no_contact_disconnect='n/a',
        no_contact_no_answer='n/a',
        no_contact_other='n/a',
        discounted_invalid_cases='1/10, 1%',
        invalid_fields="'call_end_time' column had missing data")


def test_generate_report_raises_exception(dodgy_date_value_dataframe):
    with pytest.raises(BertException) as err:
        generate_report(dodgy_date_value_dataframe,
                        "100/100",
                        "You broke it so bad DFS had to end their sale")
    assert err.value.message == "Could not calculate get_hours_worked(): '>=' not supported between instances of 'str' and 'DatetimeWithNanoseconds'"
    assert err.value.code == 400


def test_generate_report_handles_unexpected_time_totals(unexpected_time_totals_dataframe):
    with pytest.raises(BertException) as err:
        generate_report(unexpected_time_totals_dataframe, 1)
    assert err.value.message == "Hours worked (0:02:03) cannot be less than time spent on calls (1:53:20). Please review the Call History data"
    assert err.value.code == 400

def test_handle_no_contacts_breakdown(interviewer_call_pattern_report):
    df = pd.DataFrame(
        {"status": ["no contact", "no contact", "no contact", "no contact", "no contact"],
        "call_result": ["answer service", "busy", "disconnect", "no answer", "others"]},
    )
    report = handle_no_contacts_breakdown(df, interviewer_call_pattern_report)
    assert report == InterviewerCallPattern(
        hours_worked='7:24:00',
        call_time='0:00:00',
        hours_on_calls='0%',
        average_calls_per_hour=3.14,
        respondents_interviewed=5,
        average_respondents_interviewed_per_hour=123,
        refusals='foobar',
        no_contacts='foobar',
        completed_successfully='',
        appointments_for_contacts='101%',
        no_contact_answer_service='1/5, 20.0%',
        no_contact_busy='1/5, 20.0%',
        no_contact_disconnect='1/5, 20.0%',
        no_contact_no_answer='1/5, 20.0%',
        no_contact_other='1/5, 20.0%',
        discounted_invalid_cases='0',
        invalid_fields='n/a')
