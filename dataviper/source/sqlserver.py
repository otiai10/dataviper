import sys
import pypyodbc
import pandas as pd
from dataviper.logger import NaivePrintLogger
from dataviper.categorical_column import CategoricalColumn
from dataviper.report.profile import Profile
from dataviper.report.joinability import Joinability

class SQLServer():
    """
    class SQLServer is a connection provider for SQL Server
    and query builder as well.
    """

    def __init__(self, config={}, sigfig=4, logger=NaivePrintLogger()):
        self.config = config
        self.sigfig = sigfig
        self.logger = logger


    def connect(self, config):
        config = config if config is not None else self.config
        connectString = ''
        for key, value in list(config.items()):
            if value is not None:
                connectString += (key + '=' + value + ';')
        self.__conn = pypyodbc.connect(connectString)
        return self.__conn


    def get_schema(self, table_name):
        self.logger.info("START: get_schema")
        query = self.__get_schema_query(table_name)
        schema_df = pd.read_sql(query, self.__conn)
        schema_df = schema_df[['column_name', 'data_type']].set_index('column_name')
        schema_df.index = schema_df.index.str.lower()
        self.logger.info("DONE: get_schema")
        return Profile(table_name, schema_df)


    def __get_schema_query(self, table_name):
        return "SELECT * FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{}'".format(table_name)


    def count_null(self, profile):
        self.logger.info("START: count_null")
        query = self.__count_null_query(profile)
        null_count_df = pd.read_sql(query, self.__conn)
        # {{{ TODO: Separete to another method
        total = null_count_df['total'][0]
        profile.total = total
        # }}}
        null_count_df = null_count_df.drop('total', axis=1)
        null_count_df = null_count_df.T.rename(columns={0: 'null_count'})
        null_count_df['null_%'] = round((null_count_df['null_count'] / total) * 100, self.sigfig)
        profile.schema_df = profile.schema_df.join(null_count_df)
        self.logger.info("DONE: count_null")
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
        return '(SELECT COUNT(1) FROM {} WHERE [{}] is NULL) as [{}]'.format(table_name, column_name, column_name)


    def get_deviation(self, profile):
        self.logger.info("START: get_deviation")
        devis = pd.DataFrame()
        for column_name in profile.schema_df.index:
            data_type = profile.schema_df.at[column_name, 'data_type']
            if not data_type in ('int', 'float'):
                continue
            try:
                df = self.__get_deviation_df_for_a_column(profile.table_name, column_name)
                devis = devis.append(df)
            except Exception as e:
                self.logger.error("get_deviation", e)
        profile.schema_df = profile.schema_df.join(devis, how='left')
        self.logger.info("DONE: get_deviation")
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
        return 'SELECT MIN([{0}]) as min, MAX([{0}]) as max, AVG([{0}]) as avg, STDEV([{0}]) as std FROM {1}'.format(column_name, table_name)


    def get_variation(self, profile):
        self.logger.info("START: get_variation")
        variations = pd.DataFrame()
        for column_name in profile.schema_df.index:
            df = self.__get_variation_df_for_a_column(profile.table_name, column_name)
            variations = variations.append(df)
        profile.schema_df = profile.schema_df.join(variations, how='left')
        profile.schema_df['unique_%'] = round((profile.schema_df['unique_count'] / profile.total) * 100, self.sigfig)
        self.logger.info("DONE: get_variation")
        return profile


    def __get_variation_df_for_a_column(self, table_name, column_name):
        query = self.__get_variation_query_for_a_column(table_name, column_name)
        df = pd.read_sql(query, self.__conn)
        df.index = [column_name]
        return df


    def __get_variation_query_for_a_column(self, table_name, column_name):
        """
        TODO: Don't use .format, use SQL placeholder and parameter markers.
              See https://docs.microsoft.com/en-us/sql/odbc/reference/develop-app/binding-parameter-markers?view=sql-server-2017
        """
        return 'SELECT COUNT(DISTINCT [{0}]) as unique_count FROM {1}'.format(column_name, table_name)


    def get_examples(self, profile, count=8):
        self.logger.info("START: get_example")
        aggregation = pd.DataFrame(columns=['examples_top_{}'.format(count), 'examples_last_{}'.format(count)], index=profile.schema_df.index.values)
        try:
            top_df = pd.read_sql(self.__get_examples_query(profile, count=count, desc=False), self.__conn)
            for column_name in top_df.columns.values:
                aggregation.at[column_name, 'examples_top_{}'.format(count)] = top_df[column_name].values
            last_df = pd.read_sql(self.__get_examples_query(profile, count=count, desc=True), self.__conn)
            for column_name in last_df.columns.values:
                aggregation.at[column_name, 'examples_last_{}'.format(count)] = last_df[column_name].values
        except Exception as e:
            self.logger.error("get_deviation", e)
        profile.schema_df = profile.schema_df.join(aggregation, how='left')
        self.logger.info("DONE: get_example")
        return profile


    def __get_examples_query(self, profile, count=8, desc=False):
        """
        TODO: Don't use .format, use SQL placeholder and parameter markers.
              See https://docs.microsoft.com/en-us/sql/odbc/reference/develop-app/binding-parameter-markers?view=sql-server-2017
        """
        return 'SELECT TOP {0} * FROM {1} ORDER BY [{2}] {3}'.format(count, profile.table_name, self.infer_primary_key(profile), 'DESC' if desc else 'ASC')


    def infer_primary_key(self, profile):
        """
        Primary key must be picked up in purpose of sorting for "get_examples".
        The data_type "key" can be set intentionally by human modification.
        """
        if 'key' in profile.schema_df['data_type'].values:
            return profile.schema_df[profile.schema_df['data_type'] == 'key'].index[0]
        if 'date' in profile.schema_df['data_type'].values:
            return profile.schema_df[profile.schema_df['data_type'] == 'date'].index[0]
        if 'unique_count' in profile.schema_df.columns:
            return profile.schema_df['unique_count'].idxmax()
        return profile.schema_df.index[0]

    def onehot_encode(self, profile, key, categorical_columns, result_table, commit=False):
        self.logger.info("START: onehot_encode")
        profile = self.collect_category_values(profile, categorical_columns)
        targets = self.__query_for_onehot_columns(key, profile)
        query = "SELECT {0} INTO {1} FROM {2}".format(targets, result_table, profile.table_name)
        profile.onehot_table_name = result_table
        if commit:
            cur = self.__conn.cursor()
            cur.execute(query).commit()
        else:
            # Leave an executor function to Profile
            profile.do_onehot = lambda: self.__conn.cursor().execute(query).commit()
        self.logger.info("DONE: onehot_encode")
        return profile


    def __query_for_onehot_columns(self, key, profile):
        select_targets = ['[{}]'.format(key)]
        for cc in profile.categorical_columns.values():
            select_targets.append(self.cases_query_for_a_categorical_column(cc))
        return ",\n".join(select_targets)


    def collect_category_values(self, profile, categorical_columns):
        for column_name in categorical_columns:
            self.collect_category_values_on(profile, column_name)
        return profile


    def collect_category_values_on(self, profile, column_name):
        query = "SELECT DISTINCT [{0}] FROM [{1}] WHERE [{0}] IS NOT NULL".format(column_name, profile.table_name)
        df = pd.read_sql(query, self.__conn)
        # Some clean ups
        vals = list(map(lambda val: val.strip(), filter(lambda val: val, df.iloc[:, 0].tolist())))
        profile.categorical_columns[column_name] = CategoricalColumn(column_name, vals)
        return profile


    def cases_query_for_a_categorical_column(self, cat_column):
        cases = []
        for val in cat_column.values:
            query = "CASE WHEN ([{0}] = '{1}') THEN 1 ELSE 0 END AS [{0}_{1}]".format(cat_column.name, val)
            cases.append(query)
        return ",\n".join(cases)


    def joinability(self, on):
        self.logger.info("START: joinability")
        [table_x, table_y] = on.items()
        query = self.__query_for_joinability(table_x, table_y)
        df = pd.read_sql(query, self.__conn)
        m_c = df['match_count'][0]
        x_total = df['x_total'][0]
        x_drop = x_total - m_c
        y_total = df['y_total'][0]
        y_drop = y_total - m_c
        self.logger.info("DONE: joinability")
        return Joinability(
            table_x[0],
            table_y[0],
            pd.DataFrame([
                [table_x[0], table_x[1], x_total, m_c, (m_c / x_total) * 100, x_drop, (x_drop / x_total) * 100],
                [table_y[0], table_y[1], y_total, m_c, (m_c / y_total) * 100, y_drop, (y_drop / y_total) * 100]
            ], columns=['table', 'key', 'total', 'match', 'match_%', 'drop', 'drop_%']).set_index('table')
        )


    def __query_for_joinability(self, table_x, table_y):
        return '''
            SELECT
                (SELECT COUNT(1) FROM [{0}]) as x_total,
                (SELECT COUNT(1) FROM [{2}]) as y_total,
                (SELECT COUNT(1) FROM [{0}] INNER JOIN [{2}] ON [{0}].[{1}] = [{2}].[{3}]) as match_count
        '''.format(table_x[0], table_x[1], table_y[0], table_y[1]).strip()
