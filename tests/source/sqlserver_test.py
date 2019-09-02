from dataviper.source.sqlserver import SQLServer

def test_SQLServer_placeholder():
    source = SQLServer()
    assert isinstance(source, SQLServer)
