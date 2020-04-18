import os
import ast
import pandas as pd
import numpy as np
import logging
from dataviper.source.datasource import DataSource
from dataviper.report.profile import Profile
from dataviper.logger import IndentLogger

class CSV(DataSource):

    def __init__(self, logger=IndentLogger()):
        logging.warning('NOTE: CSV calc might require much memory of your computer.')
        self.logger = logger


    def get_schema(self, csv_file_name, cols=[]):
        self.logger.enter('START', 'get_schema')
        if len(cols) > 0:
            rawdata = pd.read_csv(csv_file_name, header=0, usecols=cols)
        else:
            rawdata = pd.read_csv(csv_file_name)
        # rawdata = rawdata.replace(dict((col, {np.nan: None}) for col in rawdata.columns))
        schema_df = pd.DataFrame(index=rawdata.columns, columns=['data_type'])
        for column in rawdata.columns:
            self.logger.enter('START', 'infer_data_type', column)
            schema_df['data_type'][column] = self.infer_data_type(rawdata[column])
            self.logger.exit('DONE', 'infer_data_type', column)
        table_name = os.path.basename(os.path.splitext(csv_file_name)[0])
        profile = Profile(table_name, schema_df)
        profile.rawdata = rawdata
        self.count_total(profile)
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
        self.logger.enter('START', 'count_total')
        profile.total = len(profile.rawdata)
        self.logger.exit('DONE', 'count_total')
        return profile


    def count_null(self, profile):
        self.logger.enter('START', 'count_null')
        profile.schema_df['null_count'] = 0.0
        profile.schema_df['null_%'] = 0.0
        for col in profile.rawdata.columns:
            self.logger.enter('START', 'count_null', col)
            null_count = self.__count_null_for(col, profile.rawdata[col])
            profile.schema_df.at[col, 'null_count'] = null_count
            profile.schema_df.at[col, 'null_%'] = float(null_count / profile.total) * 100
            self.logger.exit('DONE', 'count_null', col)
        self.logger.exit('DONE', 'count_null')
        return profile


    def __count_null_for(self, col, values):
        return values.isna().sum()


    def count_unique(self, profile):
        self.logger.enter('START', 'count_unique')
        profile.schema_df['unique_count'] = 0.0
        profile.schema_df['unique_%'] = 0.0
        for col in profile.rawdata.columns:
            self.logger.enter('START', 'count_unique', col)
            unique_count = profile.rawdata[col].unique().size
            profile.schema_df.at[col, 'unique_count'] = unique_count
            profile.schema_df.at[col, 'unique_%'] = float(unique_count / profile.total) * 100
            self.logger.exit('DONE', 'count_unique', col)
        self.logger.exit('DONE', 'count_unique')
        return profile


    def get_deviation(self, profile):
        self.logger.enter('START', 'get_deviation')
        profile.schema_df['min'] = np.nan
        profile.schema_df['max'] = np.nan
        profile.schema_df['avg'] = np.nan
        profile.schema_df['med'] = np.nan
        profile.schema_df['std'] = np.nan
        for col in profile.rawdata.columns:
            if profile.schema_df['data_type'][col] not in ('int', 'float'):
                continue
            self.logger.enter('START', 'get_deviation', col)
            profile.schema_df.at[col, 'min'] = profile.rawdata[col].min()
            profile.schema_df.at[col, 'max'] = profile.rawdata[col].max()
            profile.schema_df.at[col, 'avg'] = profile.rawdata[col].mean()
            profile.schema_df.at[col, 'med'] = profile.rawdata[col].median()
            profile.schema_df.at[col, 'std'] = profile.rawdata[col].std()
            self.logger.exit('DONE', 'get_deviation', col)
        self.logger.exit('DONE', 'get_deviation')
        return profile


    def get_examples(self, profile, count=5):
        profile.schema_df['top_{}_examples'.format(count)] = [[]] * len(profile.schema_df)
        profile.schema_df['last_{}_examples'.format(count)] = [[]] * len(profile.schema_df)
        for col in profile.rawdata.columns:
            profile.schema_df.at[col, 'top_{}_examples'.format(count)]  = profile.rawdata[col].head(n=count).tolist()
            profile.schema_df.at[col, 'last_{}_examples'.format(count)] = profile.rawdata[col].tail(n=count).tolist()
        return profile


    def pivot(self, profile, key, categorical_columns, result_table, **kwargs):
        logging.warning("CSV pivot is not supported yet.")
        return profile

    def joinability(self, on):
        logging.warning("CSV joinability check is not supported yet.")
        return


    def histogram(self, profile, column):
        logging.warning("CSV histogram is not supported yet.")
        return
