# dataviper

- Mono Table Data Quality Check Tool
- TODO: Multi Tables Data Quality Check

# Motivation

- Provide easy way to get the shit done
- Includ SQLServer as a data source
- Don't load whole the table on your memory

# Example

```python
from dataviper import Client
from dataviper.source import SQLServer

client = Client(source=SQLServer())

with client.connect(config) as conn:

    # Just fetch types of columns first
    schema = client.get_schema(table_name)
    # Count NULL values on each column
    client.count_null(schema)
    # Get min, med, max, std
    client.get_deviation(schema)
    # Get top 10 samples, last 10 samples,
    # number of unique values
    client.get_diversity(schema)

    # If you want pandas DataFrame and write it to a file
    schema.to_dataframe.to_csv(your_file)
```