import os
import ast
import pandas as pd
import operator
from dataviper.source.datasource import DataSource
from dataviper.report.profile import Profile
from dataviper.logger import IndentLogger

class CSV(DataSource):

    def __init__(self, logger=IndentLogger()):
        self.logger = logger


    def get_schema(self, csv_file_name, cols=[]):
        self.logger.enter('START', 'get_schema')
        if len(cols) > 0:
            rawdata = pd.read_csv(csv_file_name, header=0, usecols=cols)
        else:
            rawdata = pd.read_csv(csv_file_name)
        schema_df = pd.DataFrame(index=rawdata.columns, columns=['data_type'])
        for column in rawdata.columns:
            self.logger.enter('START', 'infer_data_type', column)
            schema_df['data_type'][column] = self.infer_data_type(rawdata[column])
            self.logger.exit('DONE', 'infer_data_type', column)
        table_name = os.path.basename(os.path.splitext(csv_file_name)[0])
        profile = Profile(table_name, schema_df)
        profile.rawdata = rawdata
        self.logger.exit('DONE', 'get_schema')
        return profile


    def infer_data_type(self, values, limit=-1):
        """
        https://docs.python.org/3/library/ast.html#ast.literal_eval
        """
        types = {}
        for val in values[:limit]:
            t = type(val)
            types[t] = types.get(t, 0) + 1
        return max(types.keys(), key=lambda k: types[k]).__name__


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


    def pivot(self, profile):
        return profile


    def joinability(self, on):
        return
