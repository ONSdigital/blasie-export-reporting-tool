import datetime

from reports.mi_hub_call_history_report import get_mi_hub_call_history
from functions.csv_functions import write_csv
from reports.mi_hub_respondent_data_report import get_mi_hub_respondent_data
from functions.google_storage_functions import init_google_storage
from functions.zip_functions import create_zip


class DeliverMIHubReportsService:
    def __init__(self, config, request_json):
        self._config = config
        self._config.log()

        self._google_storage = init_google_storage(self._config)

        self._questionnaire_name = request_json["name"]
        self._questionnaire_id = request_json["id"]

        self._mi_hub_call_history = get_mi_hub_call_history(
            self._config, self._questionnaire_name, self._questionnaire_id)

        self._mi_hub_respondent_data = get_mi_hub_respondent_data(
            self._config, self._questionnaire_name)

        self._files = []
        self._filename = self.__filename()

    def deliver_mi_hub_reports(self):
        self.__add_call_history_csv_to_list_of_files()
        self.__add_respondent_data_csv_to_list_of_files()

        if not self._files:
            return f"No MI data found for {self._questionnaire_name}. Cloud function complete"

        if self._google_storage.bucket is None:
            raise Exception(f"Connection to storage bucket {self._config.nifi_staging_bucket} failed", 500)

        zipped_data = create_zip(self._files)
        self.__upload_zip_data_to_gcp_bucket(zipped_data)
        return f"Data found and uploaded for {self._questionnaire_name}. Cloud function complete"

    def __add_call_history_csv_to_list_of_files(self):
        if self._mi_hub_call_history:
            call_history_csv = write_csv(self._mi_hub_call_history)
            self._files.append({"filename": "call_history.csv", "content": call_history_csv})
        else:
            print(f"No call history found for {self._questionnaire_name}")

    def __add_respondent_data_csv_to_list_of_files(self):
        if self._mi_hub_respondent_data:
            respondent_data_csv = write_csv(self._mi_hub_respondent_data)
            self._files.append({"filename": "respondent_data.csv", "content": respondent_data_csv})
        else:
            print(f"No respondent data found for {self._questionnaire_name}")

    def __upload_zip_data_to_gcp_bucket(self, zipped_data):
        self._google_storage.upload_zip(f"{self.__filename()}.zip", zipped_data)

    def __filename(self):
        datetime_string = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        return f"mi_{self._questionnaire_name}_{datetime_string}"
