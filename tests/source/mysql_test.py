import os
from dataviper.source import MySQL


def test_SQLServer_placeholder():
    source = MySQL()
    assert isinstance(source, MySQL)

    config = {
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv(
            'MYSQL_PASSWORD',
            os.getenv('MYSQL_ROOT_PASSWORD', '')
        ),
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'database': os.getenv('MYSQL_DATABASE', 'dataviper_test')
    }
    with source.connect(config):
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
