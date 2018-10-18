import json
import logging

from gcloud import storage
from google.auth.exceptions import DefaultCredentialsError
from oauth2client.service_account import ServiceAccountCredentials
from app.settings import DATA_DUMP_FILE_NAME, GOOGLE_APPLICATION_CREDENTIALS, \
    SERVICE_NAME, PSEUDOCONE_GCS_BUCKET, PROJECT_NAME

logger = logging.getLogger(SERVICE_NAME)


def read_table(file_name=None):

    """ Read dataset from GCP bucket.
    A json file containing service account credentials is required,
    path to file needs to be added in the environment variable
        GOOGLE_APPLICATION_CREDENTIALS
    Args:
        file_name (str): name of file stored in GCP.
    Returns:
        (bool): True, if the file was written successfully
    """

    if not GOOGLE_APPLICATION_CREDENTIALS:
        logger.warning("'GOOGLE_APPLICATION_CREDENTIALS' is not set. To read from GCP storage, this environement"
                       "variable needs to be specified. Will now try to read the file locally instead.")
        return None

    if file_name is None:
        file_name = DATA_DUMP_FILE_NAME

    bucket = get_gcp_bucket()
    if bucket:
        return get_blob(bucket, file_name)
    else:
        return None


def get_gcp_bucket():
    try:
        credentials_dict = json.load(open(GOOGLE_APPLICATION_CREDENTIALS, 'r'))
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict)
        client = storage.Client(credentials=credentials, project=PROJECT_NAME)
        bucket = client.get_bucket(PSEUDOCONE_GCS_BUCKET)
        return bucket
    except DefaultCredentialsError:
        logger.warning("Could not retrieve GCP bucket. Please check whether the credentials file is correct and "
                       "whether it contains the right permissions. Will now try to read the file locally instead.")
        return None


def get_blob(bucket, file_name):
    """ Read data as json (and convert to dict)."""
    if bucket.blob(file_name).exists():
        logger.info(f"Loading data from file {file_name} in GCP bucket {bucket}.")
        # json_dict = json.loads(bucket.blob(file_name, chunk_size=262144).download_as_string())
        json_dict = [
            json.loads(item) for item in bucket.blob(file_name, chunk_size=262144)
                                               .download_as_string()
                                               .decode('utf-8')
                                               .split('\n')
        ]
        return json_dict
    else:
        logger.warning(f"File '{file_name}' does not exist in GCP bucket. Will now try to read the file locally"
                       f" instead.")
        return None
