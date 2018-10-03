import os
from app.pseudocone_pb2 import ResourceType

SERVICE_NAME = "Pseudocone"
DEFAULT_LOG_LEVEL = "DEBUG"

ONE_DAY_IN_SECONDS = 60*60*24
DEFAULT_PERMISSABLE_RESOURCE_TYPES = [ResourceType.Value("EPISODE"), ResourceType.Value("CLIP")]

GRPC_PORT = "50057"
MAX_WORKERS = 10
REQUEST_TIMEOUT = 5

LOG_LEVEL = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCP_PROJECT_NAME = 'bbc-connected-data'
DATA_DUMP_FILE_NAME = os.getenv("DATA_DUMP_FILE_NAME", "scv_data_sample.json")

PSEUDOCONE_GCS_BUCKET = 'pseudocone_data_dump'
