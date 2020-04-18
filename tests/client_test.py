from dataviper import Client


def test_client_placeholder():
    client = Client(source=None)
    assert isinstance(client, Client)
