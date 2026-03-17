def test_package_tester_imports():
    import nodes.package_tester as m
    assert hasattr(m, "handle")
