from ..profile import Profile
import pypyodbc
import pandas as pd

class SQLServer():
    """
    class SQLServer is a connection provider for SQL Server
    and query builder as well.
    """

    def __init__(self, config=None):
        self.config = config


    def connect(self, config):
        self.__conn = pypyodbc.connect(
            driver=config.get('driver', '{ODBC Driver 17 for SQL Server}'),
            server=config.get('server', 'localhost'),
            database=config.get('database'),
            trusted_connection=config.get('use_trusted_connection', 'Yes'),
        )
        return self.__conn


    def get_schema(self, table_name):
        query = self.__get_schema_query(table_name)
        schema_df = pd.read_sql(query, self.__conn)
        schema_df = schema_df[['column_name', 'data_type']].set_index('column_name')
        schema_df.index = schema_df.index.str.lower()
        return Profile(table_name, schema_df)


    def __get_schema_query(self, table_name):
        return "SELECT * FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{}'".format(table_name)


    def count_null(self, profile):
        query = self.__count_null_query(profile)
        null_count_df = pd.read_sql(query, self.__conn)
        total = null_count_df['total'][0]
        null_count_df = null_count_df.drop('total', axis=1)
        null_count_df = null_count_df.T.rename(columns={0: 'null_count'})
        null_count_df['null_percentage'] = (null_count_df['null_count'] / total) * 100
        profile.schema_df = profile.schema_df.join(null_count_df)
        return profile


    def __count_null_query(self, profile):
        queries = ['(SELECT COUNT(1) FROM {}) as Total'.format(profile.table_name)]
        for column_name in profile.schema_df.index:
            queries += [self.__count_null_query_for_a_column(profile.table_name, column_name)]
        return 'SELECT {}'.format(', '.join(queries))


    def __count_null_query_for_a_column(self, table_name, column_name):
        """
        TODO: Don't use .format, use SQL placeholder and parameter markers.
              See https://docs.microsoft.com/en-us/sql/odbc/reference/develop-app/binding-parameter-markers?view=sql-server-2017
        """
        return '(SELECT count(1) FROM {} WHERE {} is NULL) as {}'.format(table_name, column_name, column_name)


    def get_deviation(self, profile):
        devis = pd.DataFrame()
        for column_name in profile.schema_df.index:
            data_type = profile.schema_df.at[column_name, 'data_type']
            if not data_type in ('int'):
                continue
            df = self.__get_deviation_df_for_a_column(profile.table_name, column_name)
            devis = devis.append(df)
        profile.schema_df = profile.schema_df.join(devis, how='left')
        return profile


    def __get_deviation_df_for_a_column(self, table_name, column_name):
        query = self.__get_deviation_query_for_a_column(table_name, column_name)
        df = pd.read_sql(query, self.__conn)
        df.index = [column_name]
        return df


    def __get_deviation_query_for_a_column(self, table_name, column_name):
        """
        TODO: Don't use .format, use SQL placeholder and parameter markers.
              See https://docs.microsoft.com/en-us/sql/odbc/reference/develop-app/binding-parameter-markers?view=sql-server-2017
        """
        return 'SELECT MIN({0}) as min, MAX({0}) as max, AVG({0}) as avg, STDEV({0}) as std FROM {1}'.format(column_name, table_name)