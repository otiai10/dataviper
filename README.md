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
    profile.to_csv('./{}.csv'.format(profile.table_name))
```

Then you will get `My_Table_Name.csv` which looks like

| column_name | data_type | null_count | null_% | unique_count | unique_% | min | max    | avg    | std | examples_top_8 | examples_last_8 |
|------------:|----------:|-----------:|-------:|-------------:|---------:|----:|-------:|-------:|----:|---------------:|----------------:|
| id          | int       |          0 | 0.0000 | 924305       | 100.0000 | 0   | 924304 | 462152 | 30.0 | [1,2,3,4,5,6,7,8] | [924297,924298,924299,924300,924301,924302,924303,924304]
| name        | varchar   |          0 | 0.0000 | 908230       | 98.2609 |   |  |  | | [john,mary,hiromu,jack,mike] | [sophia,victor,diana,chika,avelino]


# Data Sources

## TODO: csv

```python
from dataviper.source import CSV
client = Client(source=CSV())
```

## TODO: Excel

```python
from dataviper.source import Excel
client = Client(source=Excel())
```

## TODO: MySQL

```python
from dataviper.source import MySQL

config = {
    'server': 'mysql.my-host.com',
    'database': 'my-database',
    'user': 'hiromu',
    'pass': 'xxxxxxx',
}

client = Client(source=MySQL(config))
```