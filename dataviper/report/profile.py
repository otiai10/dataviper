import os
from dataviper.report.utils import create_workbook_from_dataframe, fill_cell_color, fill_text_color

class Profile():

    def __init__(self, table_name, schema_df):
        self.table_name = table_name
        self.schema_df = schema_df
        self.total = None
        self.categorical_columns = {} # Dict of CategoricalColumn
        self.rawdata = None # Only used by CSV source

    def to_csv(self, outdir="."):
        file_path = os.path.join(outdir, "profile_{}.csv".format(self.table_name))
        self.schema_df.to_csv(file_path)
        print("REPORT CREATED:", file_path)


    def to_excel(self, outdir='.'):
        workbook = create_workbook_from_dataframe(self.schema_df)
        self.__beautify_worksheet(workbook.active)
        filename = os.path.join(outdir, "profile_{}.xlsx".format(self.table_name))
        workbook.save(filename)
        print("REPORT CREATED:", filename)

    def __beautify_worksheet(self, ws):
        for row in list(ws.rows)[1:]: # Without the header row
            for col, cell in enumerate(row):
                if col == 1: # column_type
                    if cell.value in ('int', 'float'):
                        fill_cell_color(cell, '00FFBF')
                    elif cell.value in ('varchar', 'nvarchar', 'str'):
                        fill_cell_color(cell, 'FFBF00')
                elif col == 3: # null_%
                    if float(cell.value) >= 70:
                        fill_text_color(cell, 'FF0000')
                elif col == 5: # unique_%
                    if float(cell.value) > 99:
                        fill_text_color(cell, '0000FF', bold=True)
