from dataviper import CategoricalColumn


def test_client_placeholder():
    col = CategoricalColumn("sales_type")
    assert isinstance(col, CategoricalColumn)
