from models.interviewer_call_pattern_model import InterviewerCallPattern, InterviewerCallPatternWithNoValidData


def test_interviewer_call_pattern():
    interviewer_call_pattern = InterviewerCallPattern(
        hours_worked="",
        call_time="",
        hours_on_calls="",
        average_calls_per_hour=0.0,
        respondents_interviewed=0,
        average_respondents_interviewed_per_hour=0.0,
        refusals="",
        no_contacts="",
        answer_service="",
        busy="",
        disconnect="",
        no_answer="",
        other="",
        completed_successfully="",
        appointments_for_contacts="",
        discounted_invalid_cases="",
        invalid_fields="",
    )
    assert interviewer_call_pattern is not None


def test_interviewer_call_pattern_with_no_valid_data():
    interviewer_call_pattern_with_no_valid_data = InterviewerCallPatternWithNoValidData(
        discounted_invalid_cases="",
        invalid_fields="",
    )
    assert interviewer_call_pattern_with_no_valid_data is not None
