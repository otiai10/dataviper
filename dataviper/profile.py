
class Profile():

    def __init__(self, table_name, schema_df):
        self.table_name = table_name
        self.schema_df = schema_df


    def to_csv(self, fpath):
        self.schema_df.to_csv(fpath)
