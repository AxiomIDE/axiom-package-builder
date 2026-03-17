from nodes.code_generator import code_generator


def test_code_generator_imports():
    assert callable(code_generator)

def test_to_snake():
    from nodes.code_generator import _to_snake
    assert _to_snake("PackageBuilder") == "package_builder"
    assert _to_snake("IntentClassifier") == "intent_classifier"
