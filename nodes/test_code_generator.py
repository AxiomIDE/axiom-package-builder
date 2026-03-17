from nodes.code_generator import code_generator, _to_snake, _extract_code_block


def test_code_generator_imports():
    assert callable(code_generator)


def test_to_snake():
    assert _to_snake("PackageBuilder") == "package_builder"
    assert _to_snake("IntentClassifier") == "intent_classifier"
    assert _to_snake("AddInput") == "add_input"


def test_extract_code_block_with_fence():
    text = '```python\nprint("hello")\n```'
    result = _extract_code_block(text)
    assert result == 'print("hello")'


def test_extract_code_block_no_fence():
    text = 'some plain text'
    result = _extract_code_block(text)
    assert result == 'some plain text'


def test_extract_code_block_with_language():
    text = '```proto\nsyntax = "proto3";\n```'
    result = _extract_code_block(text)
    assert result == 'syntax = "proto3";'
