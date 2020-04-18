from dataviper.source.mysql import MySQL

def test_SQLServer_placeholder():
    source = MySQL()
    assert isinstance(source, MySQL)

    config = {'user': 'root', 'password': '', 'database': 'viper_test'}
    with source.connect(config):
        profile = source.get_schema('Sales')
        profile = source.count_null(profile)
        profile = source.count_unique(profile)
        profile = source.get_deviation(profile)
        profile = source.get_examples(profile)
        profile.to_excel()
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