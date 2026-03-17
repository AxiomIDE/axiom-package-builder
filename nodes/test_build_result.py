def test_build_result_imports():
    import nodes.build_result as m
    assert hasattr(m, "handle")
