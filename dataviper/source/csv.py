import os
from dataviper.source.datasource import DataSource
from dataviper.report.profile import Profile

class CSV(DataSource):

    def __init__(self):
        pass


    def get_schema(self, csv_file_name):
        with open(csv_file_name) as original_file:
            print(original_file)
        table_name = os.path.basename(os.path.splitext(csv_file_name)[0])
        return Profile(table_name, None)


    def count_total(self, profile):
        return profile


    def count_null(self, profile):
        return profile


    def get_deviation(self, profile):
        return profile


    def count_unique(self, profile):
        return profile


    def get_examples(self, profile):
        return profile


    def onehot_encode(self, profile):
        return profile


    def joinability(self, on):
        return
