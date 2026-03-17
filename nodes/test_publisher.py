def test_publisher_imports():
    import nodes.publisher as m
    assert hasattr(m, "publisher")
