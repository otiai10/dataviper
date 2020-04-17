from dataviper.source.mysql import MySQL

def test_SQLServer_placeholder():
    source = MySQL()
    assert isinstance(source, MySQL)

    config = {'user': 'root', 'password': ''}
    with source.connect(config):
        pass
