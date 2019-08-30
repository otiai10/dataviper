# dataviper

`dataviper` is a SQL-based tool to get the basic data preparation done in easy way, with doing

- Create "Data Profile" report of a table
- One-hot encode for "Categorical Columns" and create a "one-hot" table
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

| id | region | sales_type | price | rep_id |
|:---:|:--------:|:----------:|:---------:|:-------:|
| 1 | jp | phone | 240 | 115723 |
| 2 | us | web | 90 |    125901 |
| 3 | jp | web | 560 |     8003 |
| 4 | us | shop | 920 |  182234 |
| 5 | jp | NULL | 90 |    92231 |
| 6 | us | shop | 180 |  100425 |
| 7 | us | shop | 70 |    52934 |

do

```python
with client.connect() as conn:
    table_name = 'Sales'
    profile = client.profile(table_name, example_count=3)
    profile.to_excel()
```

then you will get `profile_Sales.xlsx` file with

| column_name | data_type | null_count | null_% | unique_count | unique_% | min | max | avg | std | example_top_3 | example_last_3 |
|:-----------:|:----------:|:----------:|:------:|:------------:|:-------:|:---:|:---:|:----:|:---:|:------------:|:--------------:|
| id         | bigint  | 0 | 0     | 7 | 100.00 | 1 | 7 | 4.0 | 2.0 | [1,2,3]         | [5,6,7]          |
| region     | varchar | 0 | 0     | 2 | 28.57  |   |   |     |     | [jp,us,jp]      | [jp,us,us]       |
| sales_type | varchar | 1 | 14.28 | 3 | 42.85  |   |   |     |     | [phone,web,web] | [None,shop,shop] |
| price      | int     | 0 | 0     | 6 | 85.71  | 70 | 920 | 307.1428 | 295.379 | [240,90,560] | [90,180,70] |
| rep_id     | int     | 0 | 0     | 7 | 100.00 | 8003 |182234 | 96778.7142 | 51195.79065 | [115723,125901,8003] | [92231,100425,52934] |

# `onehot_encode`

Spread categorical columns to N binary columns.

When you have `Sales` table like above, do

```python
with client.connect() as conn:
    table_name = 'Sales'
    key = 'id'
    categorical_columns = ['region', 'sales_type']
    profile = client.get_schema(table_name)
    client.onehot_encode(profile, key, categorical_columns)
```

then you will get `Sales_ONEHOT_YYYYmmddHHMM` table with

| id | region_jp | region_us | sales_type_phone | sales_type_web | sales_type_shop |
|:--:|:---------:|:---------:|:----------------:|:--------------:|:---------------:|
| 1  |  1        | 0         | 1                | 0              | 0               |
| 2  |  0        | 1         | 0                | 1              | 0               |
| 3  |  1        | 0         | 0                | 1              | 0               |
| 4  |  0        | 1         | 0                | 0              | 1               |
| 5  |  1        | 0         | 0                | 0              | 0               |
| 6  |  0        | 1         | 0                | 0              | 1               |
| 7  |  0        | 1         | 0                | 0              | 1               |

# `joinability`

Count how much 2 tables can be joined.

When you have `Sales` table like above, and `Reps` table like this

| id     | name    | tenure |
|:------:|:-------:|:------:|
| 8003   | Hiromu  | 9      |
| 8972   | Ochiai  | 6      |
| 52934  | Taro    | 1      |
| 92231  | otiai10 | 2      |
| 100425 | Hanako  | 7      |
| 125901 | Chika   | 3      |
| 182234 | Mary    | 5      |
| 199621 | Jack    | 1      |

do

```python
with client.connect() as conn:
    report = client.joinability(on={'Sales': 'rep_id', 'Reps': 'id'})
    report.to_excel()
```

then you will get `join_Sales_Reps.xlsx` file with

| table | total | match | match_% | drop | drop_% |
|:------:|:------:|:-----:|:------:|:-----:|:------:|
| Sales | 7 | 6 | 85.714 | 1 | 14.285 |
| Reps  | 8 | 6 | 75.00 | 2 | 25.00 |

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

    client.onehot_encode(profile, 'id', ['region', 'sales_type'])
    # Table `Sales_ONEHOT_201908291732` is created

```

# Issues and TODOs

- // TODO: Define Git Host (GitHub?)
