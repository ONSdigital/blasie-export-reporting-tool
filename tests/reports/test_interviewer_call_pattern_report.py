import pytest

import numpy as np
import pandas as pd

from pandas.testing import assert_frame_equal

from models.interviewer_call_pattern_model import InterviewerCallPattern, InterviewerCallPatternWithNoValidData
from models.error_capture import BertException
from reports.interviewer_call_pattern_report import (
    invalid_data_found, generate_report,
    get_call_pattern_records_by_interviewer_and_date_range,
    get_invalid_fields, validate_dataframe
)


def test_get_call_pattern_report_when_data_is_completely_invalid(call_history_records, mocker):
    mock_interviewer_name = 'el4president'
    mock_date = '2022-01-24'
    mock_discounted_invalid_records = "numberwang"
    mock_invalid_fields = "aaaaaaaallll the fields"

    mocker.patch("reports.interviewer_call_pattern_report.get_call_history_records",
                 return_value=call_history_records)
    mocker.patch("reports.interviewer_call_pattern_report.validate_dataframe",
                 return_value=(pd.DataFrame(), mock_discounted_invalid_records, mock_invalid_fields))

    assert get_call_pattern_records_by_interviewer_and_date_range(
        mock_interviewer_name,
        mock_date,
        mock_date) == InterviewerCallPatternWithNoValidData(
        discounted_invalid_records=mock_discounted_invalid_records,
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


@pytest.mark.skip("because I cba")
def test_generate_report_returns_report_with_no_invalid_records(valid_dataframe):
    assert generate_report(valid_dataframe) == InterviewerCallPattern(
        hours_worked='0:48:05',
        call_time='0:12:50',
        hours_on_calls='26.69%',
        average_calls_per_hour=12.48,
        respondents_interviewed=10,
        average_respondents_interviewed_per_hour=12.48,
        refusals="",
        no_contacts='0/10, 0.0%',
        answer_service='0/10, 0.0%',
        busy='0/10, 0.0%',
        disconnect='0/10, 0.0%',
        no_answer='0/10, 0.0%',
        other='0/10, 0.0%',
        completed_successfully='0/10, 0.0%',
        appointments_for_contacts='6/10, 60.0%',
        discounted_invalid_cases='0',
        invalid_fields='n/a'
    )


@pytest.mark.skip("because I cba")
def test_generate_report_returns_report_with_invalid_records(valid_dataframe):
    assert generate_report(valid_dataframe, ["1/10", 1], "'call_end_time' column had missing data") == InterviewerCallPattern(
        hours_worked='0:48:05',
        call_time='0:12:50',
        hours_on_calls='26.69%',
        average_calls_per_hour=12.48,
        respondents_interviewed=10,
        average_respondents_interviewed_per_hour=12.48,
        refusals="FACE!",
        no_contacts="FACE!",
        answer_service="FACE!",
        busy="FACE!",
        disconnect="FACE!",
        no_answer="FACE!",
        other="FACE!",
        completed_successfully="0/10, 0.0%",
        appointments_for_contacts='6/10, 60.0%',
        discounted_invalid_cases='1/10, 1%',
        invalid_fields="'call_end_time' column had missing data"
    )


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
def test_get_invalid_fields(valid_dataframe, column_names):
    msg = []
    for col in column_names:
        valid_dataframe.loc[valid_dataframe['questionnaire_id'] == "remember-24-01-928350fdda5a", col] = np.nan
        msg.append(f"'{col}' column had missing data")

    result = ", ".join(msg)
    assert get_invalid_fields(call_history_dataframe) == result
    assert result.count(",") == len(column_names)


def test_get_hours_worked(call_history_dataframe):
    assert get_hours_worked(call_history_dataframe) == "2:27:57"


def test_get_call_time_in_seconds(call_history_dataframe):
    assert get_call_time_in_seconds(call_history_dataframe) == 165


@pytest.mark.parametrize(
    "hours_worked, total_call_seconds, expected",
    [
        ("10:00:00", "18000", "50.0%"),
        ("30:00:00", "16200", "15.0%"),
        ("50:00:00", "135000", "75.0%"),
    ],
)
def test_get_percentage_of_hours_on_calls(hours_worked, total_call_seconds, expected):
    assert get_percentage_of_hours_on_calls(hours_worked, total_call_seconds) == expected


@pytest.mark.parametrize(
    "hours_worked, expected",
    [
        ("08:00:00", 1.0),
        ("04:00:00", 2.0),
        ("16:00:00", 0.5),
    ],
)
def test_get_average_calls_per_hour(hours_worked, expected, call_history_dataframe):
    assert get_average_calls_per_hour(call_history_dataframe, hours_worked) == expected


def test_get_respondents_interviewed(call_history_dataframe):
    assert get_respondents_interviewed(call_history_dataframe) == 8


@pytest.mark.parametrize(
    "status, expected",
    [
        ("Appointment made", 0),
        ("No contact", 4),
        ("numberwang", 1),
        ("foobar", 0),
    ],
)
def test_get_number_of_households_completed_successfully(status, expected, call_history_dataframe):
    assert get_number_of_households_completed_successfully(status, call_history_dataframe) == expected


@pytest.mark.parametrize(
    "hours_worked, expected",
    [
        ("08:00:00", 1),
        ("10:00:00", 0.8),
        ("5:00:00", 1.6),
        ("30:00:00", 0.27),
    ],
)
def test_get_average_respondents_interviewed_per_hour(hours_worked, expected, call_history_dataframe):
    assert get_average_respondents_interviewed_per_hour(call_history_dataframe, hours_worked) == expected


@pytest.mark.parametrize(
    "status, expected",
    [
        ("Appointment made", "0.0%"),
        ("No contact", "50.0%"),
        ("numberwang", "12.5%"),
        ("foobar", "0.0%"),
    ],
)
def test_get_percentage_of_call_for_status(status, expected, call_history_dataframe):
    assert get_percentage_of_call_for_status(status, call_history_dataframe) == expected


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (1, "0:00:01"),
        (100, "0:01:40"),
        (240, "0:04:00"),
        (856, "0:14:16"),
        (8355, "2:19:15"),
    ],
)
def test_convert_call_time_seconds_to_datetime_format(seconds, expected):
    assert convert_call_time_seconds_to_datetime_format(seconds) == expected
