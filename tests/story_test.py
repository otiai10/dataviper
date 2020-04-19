import os
import shutil
import pytest
from pathlib import Path
from dataviper import Client
from dataviper.source import CSV
from dataviper.source import MySQL

__MySQL_CONFIG__ = {
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', os.getenv('MYSQL_ROOT_PASSWORD', '')),
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DATABASE', 'dataviper_test')
}


def get_outdir():
    return os.path.join(os.path.dirname(__file__), 'data', 'out')


@pytest.fixture
def fixture_outdir():
    outdir = get_outdir()
    # shutil.rmtree(outdir, ignore_errors=True)
    Path(outdir).mkdir(exist_ok=True, parents=True)
    yield

def test_story_csv(fixture_outdir):
    outdir = os.path.join(os.path.dirname(__file__), 'data', 'out')
    shutil.rmtree(outdir, ignore_errors=True)
    Path(outdir).mkdir(exist_ok=True, parents=True)
    filename = os.path.join(os.path.dirname(__file__), 'data', 'sales_data.csv')
    client = Client(source=CSV())
    profile = client.profile(filename)
    assert profile.table_name == 'sales_data'
    profile.to_excel(outdir=outdir)
    client.pivot(profile, 'id', ['region', 'sales_type'])


def test_story_MySQL(fixture_outdir):
    outdir = get_outdir()
    client = Client(source=MySQL(__MySQL_CONFIG__))
    with client.connect():
        profile = client.profile("Sales")
        profile.to_excel(outdir=outdir)
        profile.to_csv(outdir=outdir)
