import os
from dataviper.report.utils import create_workbook_from_dataframe

class Joinability():
    """
    Representing "joinability" report for 2 tables.
    """

    def __init__(self, x_name, y_name, report_df):
        self.x = x_name
        self.y = y_name
        self.report = report_df


    def to_excel(self, outdir="."):
        workbook = create_workbook_from_dataframe(self.report)
        filename = os.path.join(outdir, "joinability_{}_{}.xlsx".format(self.x, self.y))
        workbook.save(filename)
