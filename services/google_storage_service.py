import logging

from google.cloud import storage  # type: ignore

# workaround to prevent file transfer timeouts
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB


class GoogleStorage:
    def __init__(self, nifi_staging_bucket):
        self.nifi_staging_bucket = nifi_staging_bucket
        self.bucket = None
        self.initialise_bucket_connection()

    def initialise_bucket_connection(self):
        try:
            logging.info(f"Connecting to bucket - {self.nifi_staging_bucket}")
            storage_client = storage.Client()
            self.bucket = storage_client.get_bucket(self.nifi_staging_bucket)
            logging.info(f"Connected to bucket - {self.nifi_staging_bucket}")
        except Exception as ex:
            raise Exception(f"Connection to bucket {self.nifi_staging_bucket} failed: {ex}")

    def upload_zip(self, filename, data):
        logging.info(f"Uploading {filename} to storage bucket")
        blob_destination = self.bucket.blob(filename)
        blob_destination.upload_from_string(data, content_type="application/zip")
        logging.info(f"Uploaded {filename} to storage bucket")
