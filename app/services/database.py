import isodate
import json

from datetime import datetime

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

        data_with_removed_exclusion_list = [row for row in db_table[:] if row["anon_id"] in raw_inclusion_list]

        return data_with_removed_exclusion_list

    def filter_interactions_between_dates(self,  iso_start_date, iso_duration, db_table=None):

        if db_table is None:
            db_table = self.table

        start_date_parsed = datetime.strptime(iso_start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date_parsed = start_date_parsed + isodate.parse_duration(iso_duration)

        data_filtered_for_dates = [row for row in db_table if
                                   datetime.strptime(row["activitytime"], "%Y-%m-%dT%H:%M:%S.%fZ") > start_date_parsed
                                   and datetime.strptime(row["activitytime"], "%Y-%m-%dT%H:%M:%S.%fZ") <
                                   end_date_parsed]

        return data_filtered_for_dates
