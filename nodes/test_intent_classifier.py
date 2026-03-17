import pytest
from unittest.mock import MagicMock, patch


def test_intent_classifier_imports():
    """Verify the module can be imported without errors."""
    import nodes.intent_classifier as m
    assert hasattr(m, "intent_classifier")


def test_handle_returns_package_spec():
    """IntentClassifier returns a PackageSpec-compatible object."""
    try:
        from gen.axiom_official_axiom_agent_messages_messages_pb2 import AgentRequest, PackageSpec
    except ImportError:
        pytest.skip("proto bindings not generated yet")

    with patch("anthropic.Anthropic") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text='{"name":"axiom-official/test","version":"0.1.0","language":"python","description":"test","nodes":[],"proto_content":"","axiom_yaml":""}')]
        mock_client.messages.create.return_value = mock_msg

        from nodes.intent_classifier import handle
        ctx = MagicMock()
        ctx.secrets.get.return_value = "test-key"
        req = AgentRequest(goal="build a text processor", language="python")
        result = handle(req, ctx)
        assert result.name == "axiom-official/test"
