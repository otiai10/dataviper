# dataviper

- Mono Table Data Quality Check Tool
- TODO: Multi Tables Data Quality Check

# Motivation

- Provide easy way to get the shit done
- Includ SQLServer as a data source
- Don't load whole the table on your memory

# Example

```python
from dataviper.client import Client
from dataviper.source import SQLServer

config = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'sqlserver.my-host.com',
    'database': 'my-database',
}

client = Client(source=SQLServer(config))

with client.connect() as conn:
    profile = client.profile('My_Table_Name')
    profile.schema_df.to_csv('./{}.csv'.format(profile.table_name)

```