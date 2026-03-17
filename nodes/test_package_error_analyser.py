from nodes.package_error_analyser import package_error_analyser


def test_package_error_analyser_imports():
    assert callable(package_error_analyser)
