from nodes.intent_classifier import intent_classifier


def test_intent_classifier_imports():
    assert callable(intent_classifier)
