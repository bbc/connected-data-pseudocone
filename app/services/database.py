import isodate
import json
import logging

from datetime import datetime

from app.pseudocone_pb2 import ResourceType
from app.services import gcp_bucket
from app.settings import GOOGLE_APPLICATION_CREDENTIALS
from app.settings import DATA_DUMP_FILE_NAME, SERVICE_NAME
from app.utils.mapping import get_unique_vals_for_property

logger = logging.getLogger(SERVICE_NAME)


class DatabaseClient:

    def __init__(self, table_name=None):

        self.table = self.load_data(table_name)

    def load_data(self, table_name=None):
        if not table_name:
            table_name = DATA_DUMP_FILE_NAME

        gcp_data = gcp_bucket.read_table(table_name)
        if gcp_data:
            return gcp_data
        else:
            try:
                items = []
                with open(table_name, "r") as f:
                    for line in f:
                        items.append(json.loads(line))
                logger.info(f"Call returned {len(items)} items after reading local file.")
                return items
            except FileNotFoundError:
                err_message = f"Could not read from local file {table_name}."
                logger.exception(err_message)
                raise FileNotFoundError(err_message)
            except ValueError as e:
                logger.exception(e)
                raise ValueError

    def filter_users_with_inclusion_list(self, inclusion_list, user_limit, db_table=None):
        if db_table is None:
            db_table = self.table

        if len(inclusion_list) == 0:
            raw_inclusion_list = get_unique_vals_for_property(db_table, "anon_id")
            raw_inclusion_list = raw_inclusion_list[:int(user_limit)]
        else:
            inclusion_list = inclusion_list[:int(user_limit)]
            raw_inclusion_list = [user.id for user in inclusion_list]

        data_with_inclusion_filtered = [row for row in db_table[:] if row["anon_id"] in raw_inclusion_list]
        logger.info(f"Call returned {len(data_with_inclusion_filtered)} items after filtering for inclusion list.")

        return data_with_inclusion_filtered

    def filter_interactions_between_dates(self, iso_start_date=None, iso_end_date=None, iso_duration=None,
                                          db_table=None):

        if db_table is None:
            db_table = self.table

        if iso_start_date is None and iso_end_date is None:
            raise ValueError("Must specify at least one of iso_start_date and iso_end_date.")

        if iso_duration and iso_start_date and iso_end_date:
            raise ValueError("If iso_duration is specified only one of iso_start_date and iso_end_date must be"
                             " specified.")
        if iso_duration and not iso_start_date and not iso_end_date:
            raise ValueError("If iso_duration is specified only one of iso_start_date and iso_end_date must be"
                             " specified.")

        if iso_duration:
            if iso_start_date:
                start_date_parsed = datetime.strptime(iso_start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                end_date_parsed = start_date_parsed + isodate.parse_duration(iso_duration)
                start_filtered = self.filter_with_start_date(db_table, start_date_parsed)
                start_end_filtered = self.filter_with_end_date(start_filtered, end_date_parsed)
                logger.info(f"Call returned {len(start_end_filtered)} items after filtering for start date.")

                return start_end_filtered
            else:
                end_date_parsed = datetime.strptime(iso_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                start_date_parsed = end_date_parsed - isodate.parse_duration(iso_duration)
                start_filtered = self.filter_with_start_date(db_table, start_date_parsed)
                start_end_filtered = self.filter_with_end_date(start_filtered, end_date_parsed)
                logger.info(f"Call returned {len(start_end_filtered)} items after filtering for end date.")

                return start_end_filtered
        else:
            if iso_start_date:
                start_date_parsed = datetime.strptime(iso_start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                db_table = self.filter_with_start_date(db_table, start_date_parsed)
                logger.info(f"Call returned {len(db_table)} items after filtering for start date.")

            if iso_end_date:
                end_date_parsed = datetime.strptime(iso_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                db_table = self.filter_with_end_date(db_table, end_date_parsed)
                logger.info(f"Call returned {len(db_table)} items after filtering for end date.")

            return db_table

    def filter_resource_type(self, permissable_resource_types, db_table=None):

        permissable_resource_types = [str.lower(ResourceType.Name(item)) for item in permissable_resource_types]
        if db_table is None:
            db_table = self.table

        if len(db_table) > 0:
            db_table = [item for item in db_table if item['resourcetype'] in permissable_resource_types]

        return db_table

    def limit_num_interactions(self, limit, db_table=None):

        if db_table and limit > 0:
            return db_table[:limit]
        else:
            return db_table

    def filter_with_start_date(self, data, start_date_parsed):
        filtered_data = [row for row in data if
                         datetime.strptime(row["activitytime"], "%Y-%m-%dT%H:%M:%S.%fZ") > start_date_parsed]
        return filtered_data

    def filter_with_end_date(self, data, end_date_parsed):
        filtered_data = [row for row in data if
                         datetime.strptime(row["activitytime"], "%Y-%m-%dT%H:%M:%S.%fZ") < end_date_parsed]
        return filtered_data
