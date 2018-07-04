import isodate
import json

from datetime import datetime

from app.pseudocone_pb2 import ResourceType
from app.settings import DATA_PATH
from app.utils.mapping import get_unique_vals_for_property


class database_client:

    def __init__(self, table_name=None):

        self.table = self.load_data(table_name)

    def load_data(self, table_name=None):

        if table_name is None or len(table_name) is 0:
            table_name = DATA_PATH

        with open(table_name, "r") as f:
            return json.load(f)["tmp_uas"]

    def filter_users_with_inclusion_list(self, inclusion_list, limit, db_table=None):

        if db_table is None:
            db_table = self.table

        if len(inclusion_list) == 0:
            raw_inclusion_list = get_unique_vals_for_property(db_table, "anon_id")
            raw_inclusion_list = raw_inclusion_list[:int(limit)]
        else:
            inclusion_list = inclusion_list[:int(limit)]
            raw_inclusion_list = [user.id for user in inclusion_list]

        data_with_inclusion_filtered = [row for row in db_table[:] if row["anon_id"] in raw_inclusion_list]

        if len(data_with_inclusion_filtered) == 0:
            print("No items returned as user/users specified are not available.")

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
                self.check_num_items(start_end_filtered)
                return start_end_filtered
            else:
                end_date_parsed = datetime.strptime(iso_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                start_date_parsed = end_date_parsed - isodate.parse_duration(iso_duration)
                start_filtered = self.filter_with_start_date(db_table, start_date_parsed)
                start_end_filtered = self.filter_with_end_date(start_filtered, end_date_parsed)
                self.check_num_items(start_end_filtered)
                return start_end_filtered
        else:
            if iso_start_date:
                start_date_parsed = datetime.strptime(iso_start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                db_table = self.filter_with_start_date(db_table, start_date_parsed)
            if iso_end_date:
                end_date_parsed = datetime.strptime(iso_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                db_table = self.filter_with_end_date(db_table, end_date_parsed)

            self.check_num_items(db_table)
            return db_table

    def filter_resource_type(self, permissable_resource_types, db_table=None):

        permissable_resource_types = [str.lower(ResourceType.Name(item)) for item in permissable_resource_types]
        if db_table is None:
            db_table = self.table

        if len(db_table) > 0:
            db_table = [item for item in db_table if item['resourcetype'] in permissable_resource_types]

        return db_table

    def limit_num_interactions(self, limit, db_table=None):

        if db_table:
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

    def check_num_items(self, db_table):
        if len(db_table) == 0:
            print("No items returned as none are available in dates specified.")
