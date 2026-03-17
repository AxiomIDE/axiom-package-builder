def test_package_designer_imports():
    import nodes.package_designer as m
    assert hasattr(m, "handle")
