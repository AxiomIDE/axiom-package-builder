from nodes.publisher import publisher


def test_publisher_imports():
    assert callable(publisher)
