from datetime import datetime

class Client():
    """
    Client is just a proxy for data source.
    """

    def __init__(self, source=None):
        self.source = source


    def connect(self, config=None):
        return self.source.connect(config)


    def get_schema(self, table_name):
        return self.source.get_schema(table_name)


    def count_null(self, profile):
        return self.source.count_null(profile)


    def get_variation(self, profile):
        return self.source.get_variation(profile)


    def get_deviation(self, profile):
        return self.source.get_deviation(profile)


    def get_examples(self, profile):
        return self.source.get_examples(profile)


    def profile(self, table_name):
        profile = self.get_schema(table_name)
        self.count_null(profile)
        self.get_variation(profile)
        self.get_deviation(profile)
        self.get_examples(profile)
        return profile


    def pivot(self, profile, key, categorical_columns, result_table=None):
        if result_table is None:
            now = datetime.now().strftime("%Y%m%d%H%M")
            result_table = "{}_pivot_{}".format(profile.table_name, now)
        profile = self.source.pivot(profile, key, categorical_columns, result_table)
        return profile
