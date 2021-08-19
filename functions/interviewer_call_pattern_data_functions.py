import datetime

from models.error_capture import BertException


def get_hours_worked(call_history_dataframe):
    try:
        # group by date
        daily_call_history_by_date = call_history_dataframe.groupby(
            [call_history_dataframe['call_start_time'].dt.date]).agg({'call_start_time': min, 'call_end_time': max})

        # subtract first call time from last call time
        daily_call_history_by_date['hours_worked'] = daily_call_history_by_date['call_end_time'] - \
                                                     daily_call_history_by_date['call_start_time']

        # sum total hours
        total_hours = daily_call_history_by_date['hours_worked'].sum()
    except Exception as err:
        raise BertException(f"Could not calculate get_hours_worked(): {err}", 400)

    # return sum total in fancy format
    return str(datetime.timedelta(seconds=total_hours.total_seconds()))


def get_call_time_in_seconds(call_history_dataframe):
    try:
        result = round(call_history_dataframe['dial_secs'].sum())
    except Exception as err:
        raise BertException(f"Could not calculate get_call_time_in_seconds(): {err}", 400)
    return result


def convert_seconds_to_datetime_format(seconds):
    try:
        result = str(datetime.timedelta(seconds=seconds))
    except Exception as err:
        raise BertException(f"Could not convert_call_time_seconds_to_datetime_format(): {err}", 400)
    return result


def hours_on_calls(hours_worked, total_call_seconds):
    try:
        value = 100 * float(total_call_seconds) / float(get_total_seconds_from_string(hours_worked))
        result = f"{round(value, 2)}%"
    except Exception as err:
        raise BertException(f"Could not calculate get_percentage_of_hours_on_calls(): {err}", 400)
    return result


def get_total_seconds_from_string(hours_worked):
    try:
        h, m, s = hours_worked.split(':')
        result = int(h) * 3600 + int(m) * 60 + int(s)
    except Exception as err:
        raise BertException(f"Could not calculate get_total_seconds_from_string(): {err}", 400)
    return result


def average_calls_per_hour(call_history_dataframe, string_hours_worked):
    try:
        integer_hours_worked = get_total_seconds_from_string(string_hours_worked) / 3600
        total_calls = len(call_history_dataframe.index)

        result = round(total_calls / integer_hours_worked, 2)
    except Exception as err:
        raise BertException(f"Could not calculate get_average_calls_per_hour(): {err}", 400)
    return result


def respondents_interviewed(call_history_dataframe):
    try:
        result = round(call_history_dataframe['number_of_interviews'].sum())
    except Exception as err:
        raise BertException(f"Could not calculate get_respondents_interviewed(): {err}", 400)
    return result


def average_respondents_interviewed_per_hour(call_history_dataframe, string_hours_worked):
    try:
        integer_hours_worked = get_total_seconds_from_string(string_hours_worked) / 3600
        respondents_interviewed = call_history_dataframe['number_of_interviews'].sum()
        result = round(respondents_interviewed / integer_hours_worked, 2)
    except Exception as err:
        raise BertException(f"Could not calculate get_average_respondents_interviewed_per_hour(): {err}", 400)
    return result


def results_for_calls_with_status(column_name, status, valid_df, denominator):
    try:
        numerator = valid_df[column_name].str.contains(status, case=False, na=False).sum()
        percentage = 100 * numerator / denominator
    except Exception as err:
        raise BertException(f"Could not calculate the total for status containing '{status}': {err}", 400)
    return f"{numerator}/{denominator}", round(percentage, 2)
