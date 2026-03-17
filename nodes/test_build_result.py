from nodes.build_result import build_result


def test_build_result_imports():
    assert callable(build_result)
