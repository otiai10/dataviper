import os

class Profile():

    def __init__(self, table_name, schema_df):
        self.table_name = table_name
        self.schema_df = schema_df


    def to_csv(self, outdir="."):
        file_path = os.path.join(outdir, "profile_{}.csv".format(self.table_name))
        self.schema_df.to_csv(file_path)


    def to_excel(self, outdir='.'):
        file_path = os.path.join(outdir, "profile_{}.xlsx".format(self.table_name))
        self.schema_df.to_excel(file_path)
