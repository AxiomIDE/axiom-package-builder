from nodes.package_tester import package_tester


def test_package_tester_imports():
    assert callable(package_tester)
