from nodes.package_designer import package_designer


def test_package_designer_imports():
    assert callable(package_designer)
