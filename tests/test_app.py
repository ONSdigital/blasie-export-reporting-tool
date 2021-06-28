import json
from unittest.mock import patch
from models.interviewer_pattern import InterviewerPatternReport

#
# @patch("app.app.get_call_history_records_by_interviewer_and_date_range")
# def test_call_history_report_handles_missing_end_date(
#     mock_get_call_history_records_by_interviewer_and_date_range, client
# ):
#     mock_get_call_history_records_by_interviewer_and_date_range.return_value = None, []
#
#     response = client.get("/api/reports/call-history/matpal?start-date=now")
#     assert response.status_code == 400
#     assert json.loads(response.get_data(as_text=True)) == {
#         "error": "Invalid request missing required filter properties"
#     }
#
#
# @patch("app.app.get_call_history_records_by_interviewer_and_date_range")
# def test_call_history_report_handles_missing_start_date(
#     mock_get_call_history_records_by_interviewer_and_date_range, client
# ):
#     mock_get_call_history_records_by_interviewer_and_date_range.return_value = None, []
#
#     response = client.get("/api/reports/call-history/matpal?end-date=later")
#     assert response.status_code == 400
#     assert json.loads(response.get_data(as_text=True)) == {
#         "error": "Invalid request missing required filter properties"
#     }
#
#
# @patch("app.app.get_call_history_records_by_interviewer_and_date_range")
# def test_call_history_report_returns_error_on_no_records_found(
#         mock_get_call_history_records_by_interviewer_and_date_range, client
# ):
#     mock_get_call_history_records_by_interviewer_and_date_range.return_value = ("Crappy message", 400), []
#
#     response = client.get('/api/reports/call-history/matpal?start-date=2029-05-09&end-date=2029-06-14')
#     assert response.status_code == 500
#     assert response.get_data(as_text=True) == []
#
#
# @patch("app.app.get_call_history_records_by_interviewer_and_date_range")
# def test_call_history_report_returns_data_on_successful(
#         mock_get_call_history_records_by_interviewer_and_date_range, client
# ):
#     mock_get_call_history_records_by_interviewer_and_date_range.return_value = None, []
#
#     response = client.get('/api/reports/call-history/matpal?start-date=now&end-date=later')
#     assert response.status_code == 200
#     assert json.loads(response.get_data(as_text=True)) == []
#
#
@patch("app.app.get_call_pattern_records_by_interviewer_and_date_range")
def test_call_pattern_report_returns_data_on_successful(
        mock_get_call_pattern_records_by_interviewer_and_date_range, client, mock_report
):
    mock_get_call_pattern_records_by_interviewer_and_date_range.return_value = (None, 200), mock_report

    response = client.get('/api/reports/call-pattern/matpal?start-date=2021-05-09&end-date=2021-06-14')

    assert response.status_code == 200
    assert response.get_data(as_text=True) == mock_report.json()
