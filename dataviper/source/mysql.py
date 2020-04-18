import pandas as pd
from dataviper.logger import IndentLogger
from dataviper.report.profile import Profile
from dataviper.source.datasource import DataSource

import pymysql


class MySQL(DataSource):
    """
    class MySQL is a connection provider for MySQL
    and query builder as well.
    """

    def __init__(self, config={}, sigfig=4, logger=IndentLogger()):
        self.config = config
        self.sigfig = sigfig
        self.logger = logger

    def connect(self, config=None):
        config = config if config is not None else self.config
        self.__conn = pymysql.connect(**config)
        return self.__conn

    def get_schema(self, table_name):
        self.logger.enter("START: get_schema")
        query = self.__get_schema_query(table_name)
        schema_df = pd.read_sql(query, self.__conn)
        schema_df = schema_df[['column_name', 'data_type']].set_index('column_name')
        schema_df.index = schema_df.index.str.lower()
        profile = Profile(table_name, schema_df)
        profile = self.count_total(profile)
        self.logger.exit("DONE: get_schema")
        return profile

    def count_total(self, profile):
        self.logger.enter("START: count_total")
        query = "SELECT COUNT(*) AS total FROM {}".format(profile.table_name)
        df = pd.read_sql(query, self.__conn)
        profile.total = int(df['total'][0])
        self.logger.exit("DONE: count_total")
        return profile

    def __get_schema_query(self, table_name):
        return '''
            SELECT
                COLUMN_NAME as column_name,
                COLUMN_TYPE as data_type
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='{}'
        '''.format(table_name).strip()

    def count_null(self, profile):
        self.logger.enter("START: count_null")
        if profile.total is None:
            profile = self.count_total(profile)
        query = self.__count_null_query(profile)
        null_count_df = pd.read_sql(query, self.__conn)
        null_count_df = null_count_df.T.rename(columns={0: 'null_count'})
        null_count_df['null_%'] = round((null_count_df['null_count'] / profile.total) * 100, self.sigfig)
        profile.schema_df = profile.schema_df.join(null_count_df)
        self.logger.exit("DONE: count_null")
        return profile

    def __count_null_query(self, profile):
        queries = []
        for column_name in profile.schema_df.index:
            queries += [self.__count_null_query_for_a_column(profile.table_name, column_name, profile.total)]
        return 'SELECT\n{0}\nFROM {1}'.format(',\n'.join(queries), profile.table_name)

    def __count_null_query_for_a_column(self, table_name, column_name, total):
        """
        TODO: Don't use .format, use SQL placeholder and parameter markers.
              See https://docs.microsoft.com/en-us/sql
                    /odbc/reference/develop-app/binding-parameter-markers?view=sql-server-2017
        """
        return '{0} - COUNT({1}) AS {1}'.format(total, column_name)

    def get_deviation(self, profile):
        self.logger.enter("START: get_deviation")
        devis = pd.DataFrame()
        for column_name in profile.schema_df.index:
            data_type = profile.schema_df.at[column_name, 'data_type']
            df = self.__get_deviation_df_for_a_column(profile.table_name, column_name, data_type)
            if df is not None:
                devis = devis.append(df, sort=False)
        profile.schema_df = profile.schema_df.join(devis, how='left')
        self.logger.exit("DONE: get_deviation")
        return profile

    def __get_deviation_df_for_a_column(self, table_name, column_name, data_type='int'):
        if all(not data_type.startswith(t) for t in (
            'int', 'bigint', 'float', 'date', 'datetime', 'bit', 'varchar', 'nvarchar'
        )):
            self.logger.info("PASS:", column_name, "because it's {}".format(data_type))
            return
        try:
            self.logger.enter("START:", column_name, data_type)
            query = self.__get_deviation_query_for_a_column(table_name, column_name, data_type)
            df = pd.read_sql(query, self.__conn)
            df.index = [column_name]
            return df
        except Exception as e:
            self.logger.error("get_deviation", e)
        finally:
            self.logger.exit("DONE:", column_name)
        return None

    def __get_deviation_query_for_a_column(self, table_name, column_name, data_type):
        """
        TODO: Don't use .format, use SQL placeholder and parameter markers.
              See https://docs.microsoft.com/en-us/sql
                    /odbc/reference/develop-app/binding-parameter-markers?view=sql-server-2017
        """
        if any(data_type.startswith(t) for t in ('bigint', 'int', 'float', 'bit')):
            return '''
                SELECT
                    MIN({0}) as min,
                    MAX({0}) as max,
                    AVG({0}) as avg,
                    STD({0}) as std
                FROM {1}
            '''.format(column_name, table_name).strip()
        if any(data_type.startswith(t) for t in ('datetime')):
            return '''
                SELECT
                    MIN({0}) as min,
                    MAX({0}) as max,
                    CAST(AVG({0}) AS DATETIME) as avg
                FROM {1}
            '''.format(column_name, table_name).strip()
        if any(data_type.startswith(t) for t in ('date')):
            return '''
                SELECT
                    MIN({0}) as min,
                    MAX({0}) as max,
                    CAST(AVG({0}) AS DATE) as avg
                FROM {1}
            '''
        return '''
            SELECT
                MIN({0}) as min,
                MAX({0}) as max
            FROM {1}
        '''.format(column_name, table_name).strip()

    def count_unique(self, profile):
        self.logger.enter("START: count_unique")
        if profile.total is None:
            profile = self.count_total(profile)
        variations = pd.DataFrame()
        for column_name in profile.schema_df.index:
            self.logger.enter("START:", column_name)
            df = self.__count_unique_df_for_a_column(profile.table_name, column_name)
            variations = variations.append(df)
            self.logger.exit("DONE:", column_name)
        profile.schema_df = profile.schema_df.join(variations, how='left')
        profile.schema_df['unique_%'] = round((profile.schema_df['unique_count'] / profile.total) * 100, self.sigfig)
        self.logger.exit("DONE: count_unique")
        return profile

    def __count_unique_df_for_a_column(self, table_name, column_name):
        query = self.__count_unique_query_for_a_column(table_name, column_name)
        df = pd.read_sql(query, self.__conn)
        df.index = [column_name]
        return df

    def __count_unique_query_for_a_column(self, table_name, column_name):
        """
        TODO: Don't use .format, use SQL placeholder and parameter markers.
              See https://docs.microsoft.com/en-us/sql
                    /odbc/reference/develop-app/binding-parameter-markers?view=sql-server-2017
        """
        return 'SELECT COUNT(DISTINCT {0}) as unique_count FROM {1}'.format(column_name, table_name)

    def get_examples(self, profile, count=8):
        self.logger.enter("START: get_examples")
        aggregation = pd.DataFrame(
            columns=['examples_top_{}'.format(count), 'examples_last_{}'.format(count)],
            index=profile.schema_df.index.values
        )
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
        self.logger.exit("DONE: get_examples")
        return profile

    def __get_examples_query(self, profile, count=8, desc=False):
        # """
        # TODO: Don't use .format, use SQL placeholder and parameter markers.
        #       See https://docs.microsoft.com/en-us/sql
        #             /odbc/reference/develop-app/binding-parameter-markers?view=sql-server-2017
        # """
        return 'SELECT * FROM {1} ORDER BY {2} {3} LIMIT {0}'.format(
            count,
            profile.table_name,
            self.infer_primary_key(profile),
            'DESC' if desc else 'ASC'
        )

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

    def pivot(self, profile, key, categorical_columns, result_table, commit=False):
        # self.logger.enter("START: pivot")
        # profile = self.collect_category_values(profile, categorical_columns)
        # targets = self.__query_for_onehot_columns(key, profile)
        # query = "SELECT\n{0}\nINTO {1}\nFROM {2}".format(targets, result_table, profile.table_name)
        # if commit:
        #     cur = self.__conn.cursor()
        #     cur.execute(query).commit()
        # else:
        #     with open('{}.sql'.format(result_table), 'wb') as f:
        #         f.write(query.encode())
        # self.logger.exit("DONE: pivot")
        # return profile
        pass

    def __query_for_onehot_columns(self, key, profile):
        # if type(key) is str:
        #     select_targets = ['[{}]'.format(key)]
        # elif type(key) is list:
        #     select_targets = list(map(lambda k: '[{}]'.format(k), key))
        # for cc in profile.categorical_columns.values():
        #     select_targets.append(self.cases_query_for_a_categorical_column(cc))
        # return ",\n".join(select_targets)
        pass

    def collect_category_values(self, profile, categorical_columns):
        # for column_name in categorical_columns:
        #     self.collect_category_values_on(profile, column_name)
        # return profile
        pass

    def collect_category_values_on(self, profile, column_name):
        # query = "SELECT DISTINCT [{0}] FROM [{1}] WHERE [{0}] IS NOT NULL".format(column_name, profile.table_name)
        # df = pd.read_sql(query, self.__conn)
        # # Some clean ups
        # vals = list(map(lambda val: val.strip(), filter(lambda val: val, df.iloc[:, 0].tolist())))
        # profile.categorical_columns[column_name] = CategoricalColumn(column_name, vals)
        # return profile
        pass

    def cases_query_for_a_categorical_column(self, cat_column):
        # cases = []
        # for val in cat_column.values:
        #     query = "CASE WHEN ([{0}] = '{1}') THEN 1 ELSE 0 END AS [{0}_{1}]".format(cat_column.name, val)
        #     cases.append(query)
        # return ",\n".join(cases)
        pass

    def joinability(self, on):
        # self.logger.enter("START: joinability")
        # [table_x, table_y] = on.items()
        # query = self.__query_for_joinability(table_x, table_y)
        # df = pd.read_sql(query, self.__conn)
        # m_c = df['match_count'][0]
        # x_total = df['x_total'][0]
        # x_drop = x_total - m_c
        # y_total = df['y_total'][0]
        # y_drop = y_total - m_c
        # self.logger.exit("DONE: joinability")
        # return Joinability(
        #     table_x,
        #     table_y,
        #     pd.DataFrame([
        #         [table_x[0], table_x[1], x_total, m_c, (m_c / x_total) * 100, x_drop, (x_drop / x_total) * 100],
        #         [table_y[0], table_y[1], y_total, m_c, (m_c / y_total) * 100, y_drop, (y_drop / y_total) * 100]
        #     ], columns=['table', 'key', 'total', 'match', 'match_%', 'drop', 'drop_%']).set_index('table')
        # )
        pass

    def __query_for_joinability(self, table_x, table_y):
        # if type(table_x[1]) is str and type(table_y[1]) is str:
        #     return '''
        #         SELECT
        #             (SELECT COUNT(1) FROM [{0}]) as x_total,
        #             (SELECT COUNT(1) FROM [{2}]) as y_total,
        #             (SELECT COUNT(1) FROM [{0}] INNER JOIN [{2}] ON [{0}].[{1}] = [{2}].[{3}]) as match_count
        #     '''.format(table_x[0], table_x[1], table_y[0], table_y[1]).strip()
        # elif type(table_x[1]) is list
        #   and type(table_y[1]) is list
        #   or type(table_y[1]) is tuple and type(table_y[1]) is tuple:
        #
        #     keys = []
        #     for (i, k_x) in enumerate(table_x[1]):
        #         k_y = table_y[i]
        #         keys.append('[{}].[{}] = [{}].[{}]'.format(table_x[0], k_x, table_y[0], k_y))
        #     return '''
        #         SELECT
        #             (SELECT COUNT(1) FROM [{0}]) as x_total,
        #             (SELECT COUNT(1) FROM [{1}]) as y_total,
        #             (SELECT COUNT(1) FROM [{0}] INNER JOIN [{1}] ON {2}) as match_count
        #     '''.format(table_x[0], table_y[0], ' AND '.join(keys)).strip()
        # else:
        #     raise Exception("unsupported type combinations on keys: {} and {}", type(table_x[1]), type(table_y[1]))
        pass

    def histogram(self, profile, column):
        # query = self.__query_for_range(profile, column)
        # df = pd.read_sql(query, self.__conn)
        # df.index = [column]
        # return Histogram()
        pass

    def __query_for_range(self, profile, column_name, data_type=None):
        # return '''
        #     SELECT
        #         MIN([{1}]) AS min,
        #         MAX([{1}]) AS max,
        #         CAST(MAX([{1}]) AS FLOAT) - CAST(MIN[{1}] AS FLOAT) AS dif
        #     FROM [{0}]
        # '''.format(profile.table_name, column_name)
        pass
