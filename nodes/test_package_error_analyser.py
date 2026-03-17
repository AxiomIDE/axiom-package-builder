def test_package_error_analyser_imports():
    import nodes.package_error_analyser as m
    assert hasattr(m, "package_error_analyser")
