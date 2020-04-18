import os
import shutil
from pathlib import Path
from dataviper.client import Client
from dataviper.source.csv import CSV


def test_story_csv():
    outdir = os.path.join(os.path.dirname(__file__), 'data', 'out')
    shutil.rmtree(outdir, ignore_errors=True)
    Path(outdir).mkdir(exist_ok=True, parents=True)
    filename = os.path.join(os.path.dirname(__file__), 'data', 'sales_data.csv')
    client = Client(source=CSV())
    profile = client.profile(filename)
    assert profile.table_name == 'sales_data'
    profile.to_excel(outdir=outdir)
    client.pivot(profile, 'id', ['region', 'sales_type'])
