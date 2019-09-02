import os
from dataviper.client import Client
from dataviper.source import CSV

def test_story_csv():
    filename = os.path.join(os.path.dirname(__file__), 'data', 'sales_data.csv')
    client = Client(source=CSV())
    profile = client.profile(filename)
    assert profile.table_name == 'sales_data'
