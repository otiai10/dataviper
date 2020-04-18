from datetime import datetime


class Client():
    """
    Client is just a proxy for data source.
    """

    def __init__(self, source=None):
        self.source = source

    def connect(self, config=None):
        return self.source.connect(config)

    def get_schema(self, table_name, **kwargs):
        return self.source.get_schema(table_name, **kwargs)

    def count_null(self, profile):
        return self.source.count_null(profile)

    def count_unique(self, profile):
        return self.source.count_unique(profile)

    def get_deviation(self, profile):
        return self.source.get_deviation(profile)

    def get_examples(self, profile):
        return self.source.get_examples(profile)

    def profile(self, table_name, **kwargs):
        profile = self.get_schema(table_name, **kwargs)
        self.count_null(profile)
        self.count_unique(profile)
        self.get_deviation(profile)
        self.get_examples(profile)
        return profile

    def pivot(self, profile, key, categorical_columns, result_table=None, commit=False):
        if result_table is None:
            now = datetime.now().strftime("%Y%m%d%H%M")
            result_table = "{}_PIVOT_{}".format(profile.table_name, now)
        profile = self.source.pivot(profile, key, categorical_columns, result_table, commit=commit)
        return profile

    def joinability(self, on):
        if type(on) is not dict:
            raise Exception('"on" parameter MUST be a dict of [table_name]:[key], but got {}'.format(type(on)))
        if len(on.keys()) != 2:
            raise Exception('Joinability between 2 tables is supported for now, but got {}'.format(len(on.keys())))
        invalid_keys = list(filter(lambda keys: type(keys) not in (tuple, str), on.values()))
        if len(invalid_keys) > 0:
            raise Exception(
                'Keys to be joined on MUST be either of tuple or str, but got {}'.format(type(list(invalid_keys)[0]))
            )
        return self.source.joinability(on)

    def histogram(self, profile, column):
        return self.source.histogram(profile, column)
