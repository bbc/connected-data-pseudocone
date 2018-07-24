import json
import os

from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials


def read_table(file_name=None):
    """ Store scoring results on GCP in the datalab-justicia bucket.
    A json file containing service account credentials is required,
    path to file needs to be added in the environment variable
        GOOGLE_APPLICATION_CREDENTIALS
    Args:
        results_dict (dict): The results returned from metrics
        file_name (str): Path to json file to be stored on gcp bucket.
    Returns:
        (bool): True, if the file was written successfully
    """
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        return None

    if file_name is None:
        file_name = 'anonymised_uas_extract.json'

    bucket = get_gcp_bucket()

    return get_blob(bucket, file_name)


def get_gcp_bucket():
    credentials_file = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    credentials_dict = json.load(open(credentials_file, 'r'))
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict)
    client = storage.Client(credentials=credentials, project='bbc-connected-data')
    bucket = client.get_bucket('pseudocone_data_dump')
    return bucket


def get_blob(bucket, file_name):
    """ Read data as json (and convert to dict)."""
    if bucket.blob(file_name).exists():
        json_dict = json.loads(bucket.blob(file_name).download_as_string())
        return json_dict
    else:
        return None


def delete_blob(bucket, file_name):
    """ Deletes a blob from the bucket."""
    if bucket.blob(file_name).exists():
        bucket.blob(file_name).delete()
