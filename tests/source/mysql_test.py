import os
import pytest
from dataviper.source import MySQL

__MySQL_CONFIG__ = {
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', os.getenv('MYSQL_ROOT_PASSWORD', '')),
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DATABASE', 'dataviper_test')
}


@pytest.fixture
def fixture_Sales_table():
    import pymysql
    sql_file_path = os.path.join(os.getcwd(), "tests", "data", "mysql", "Sales.sql")
    lines = []
    with open(sql_file_path) as sql_file:
        lines = sql_file.read().split(';')
    conn = pymysql.connect(**__MySQL_CONFIG__)
    try:
        with conn.cursor() as cur:
            for line in lines:
                cur.execute(line)
            yield
    finally:
        # conn.cursor().execute('DROP TABLE Sales')
        conn.close()


def test_MySQL_profile(fixture_Sales_table):
    config = __MySQL_CONFIG__

    source = MySQL(config)
    assert isinstance(source, MySQL)

    with source.connect():
        profile = source.get_schema('Sales')
        profile = source.count_null(profile)
        profile = source.count_unique(profile)
        profile = source.get_deviation(profile)
        profile = source.get_examples(profile)
        # profile.to_excel()
        assert profile.schema_df.columns.tolist() == [
            'data_type',
            'null_count',
            'null_%',
            'unique_count',
            'unique_%',
            'min',
            'max',
            'avg',
            'std',
            'examples_top_8',
            'examples_last_8'
        ]
