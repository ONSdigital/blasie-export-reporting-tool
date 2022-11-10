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
            print(f"Connecting to bucket - {self.nifi_staging_bucket}")
            storage_client = storage.Client()
            self.bucket = storage_client.get_bucket(self.nifi_staging_bucket)
            print(f"Connected to bucket - {self.nifi_staging_bucket}")
        except Exception as ex:
            print("Connection to bucket failed - %s", ex)

    def upload_file(self, source, dest):
        blob_destination = self.bucket.blob(dest)
        print(f"Uploading file to storage bucket - {source}")
        blob_destination.upload_from_filename(source)
        print(f"Uploaded file to storage bucket - {source}")

    def upload_zip(self, dest, data):
        blob_destination = self.bucket.blob(dest)
        print(f"Uploading file to storage bucket - {dest}")
        blob_destination.upload_from_string(data, content_type="application/zip")
        print(f"Uploaded file to storage bucket - {dest}")
