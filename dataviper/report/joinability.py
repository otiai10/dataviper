import os
from matplotlib import pyplot
from matplotlib_venn import venn2
from dataviper.report.utils import create_workbook_from_dataframe


class Joinability():
    """
    Representing "joinability" report for 2 tables.
    """

    def __init__(self, table_x, table_y, report_df):
        self.x = table_x
        self.y = table_y
        self.report = report_df

    def to_excel(self, outdir="."):
        workbook = create_workbook_from_dataframe(self.report)
        filename = os.path.join(outdir, "joinability_{}_{}.xlsx".format(self.x[0], self.y[0]))
        workbook.save(filename)
        print("REPORT CREATED:", filename)

    def to_venn(self, outdir="."):
        (x_name, x_keys) = self.x
        (y_name, y_keys) = self.y
        (x_drop, y_drop) = self.report['drop']
        (x_drop_pc, y_drop_pc) = self.report['drop_%']
        (x_match_pc, y_match_pc) = self.report['match_%']
        match = self.report['match'][0]
        x_label = '{}\n{:g}% ({:g}%)'.format(x_name, x_match_pc, x_drop_pc)
        y_label = '{}\n{:g}% ({:g}%)'.format(y_name, y_match_pc, y_drop_pc)
        venn2(subsets=(x_drop, y_drop, match), set_labels=(x_label, y_label))
        pyplot.title('{} ({}) x {} ({})'.format(x_name, x_keys, y_name, y_keys))
        filename = os.path.join(outdir, "joinability_{}_{}.png".format(x_name, y_name))
        pyplot.savefig(filename)
        print("REPORT CREATED:", filename)
