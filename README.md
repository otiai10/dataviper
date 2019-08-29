# dataviper

`dataviper` is a SQL-based tool to get the basic data preparation done in easy way, with doing

- Create "Data Profile" report of a table
- Pivot "Categorical Columns" and create another table
- // TODO: and more

# Connection

You can choose your data source from

- [x] SQL Server
- [ ] MySQL
- [ ] PostgreSQL
- [ ] CSV
- [ ] Excel

```python
from dataviper.source import SQLServer
from dataviper.client import Client

source = SQLServer(your_config)
client = Client(source=source)
```

# `profile`

Create "Data Profile" excel file of a specified table.

When you have `Sales` table like this

| id | region | sales_type | price |
|:---:|:--------:|:----------:|:---------:|
| 1 | jp | phone | 240 |
| 2 | us | web | 90 |
| 3 | jp | web | 560 |
| 4 | us | shop | 920 |
| 5 | jp | NULL | 90 |
| 6 | us | shop | 180 |
| 7 | us | shop | 70 |

do

```python
with client.connect() as conn:
    table_name = 'Sales'
    profile = client.profile(table_name, example_count=3)
    profile.to_excel()
```

then you will get `profile_Sales.xlsx` with

| column_name | data_type | null_count | null_% | unique_count | unique_% | min | max | avg | std | example_top_3 | example_last_3 |
|:-----------:|:----------:|:----------:|:------:|:------------:|:-------:|:---:|:---:|:----:|:---:|:------------:|:--------------:|
| id         | bigint  | 0 | 0     | 7 | 100.00 | 1 | 7 | 4.0 | 2.0 | [1,2,3]         | [5,6,7]          |
| region     | varchar | 0 | 0     | 2 | 28.57  |   |   |     |     | [jp,us,jp]      | [jp,us,us]       |
| sales_type | varchar | 1 | 14.28 | 3 | 42.85  |   |   |     |     | [phone,web,web] | [None,shop,shop] |
| price      | int     | 0 | 0     | 6 | 85.71  | 70 | 920 | 307.1428 | 295.379 | [240,90,560] | [90,180,70] |

# `pivot`

Spread categorical columns to N binary columns.

When you have `Sales` table like this

| id | region | sales_type | price |
|:---:|:--------:|:----------:|:----:|
| 1 | jp | phone | 240 |
| 2 | us | web | 90 |
| 3 | jp | web | 560 |
| 4 | us | shop | 920 |
| 5 | jp | NULL | 90 |
| 6 | us | shop | 180 |
| 7 | us | shop | 70 |

do

```python
with client.connect() as conn:
    table_name = 'Sales'
    key = 'id'
    categorical_columns = ['region', 'sales_type']
    profile = client.get_schema(table_name)
    client.pivot(profile, key, categorical_columns)
```

then you will get `Sales_pivot_YYYYmmddHHMM` table with

| id | region_jp | region_us | sales_type_phone | sales_type_web | sales_type_shop |
|:--:|:---------:|:---------:|:----------------:|:--------------:|:---------------:|
| 1  |  1        | 0         | 1                | 0              | 0               |
| 2  |  0        | 1         | 0                | 1              | 0               |
| 3  |  1        | 0         | 0                | 1              | 0               |
| 4  |  0        | 1         | 0                | 0              | 1               |
| 5  |  1        | 0         | 0                | 0              | 0               |
| 6  |  0        | 1         | 0                | 0              | 1               |
| 7  |  0        | 1         | 0                | 0              | 1               |


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

    profile = client.profile('Sales')
    profile.to_excel()
    # File `profile_Sales.xlsx` is created

    client.pivot(profile, 'id', ['region', 'sales_type'])
    # Table `Sales_pivot_201908291732` is created

```

# Issues and TODOs

- // TODO: Define Git Host (GitHub?)
