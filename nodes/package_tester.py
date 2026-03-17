import os
import uuid

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import PackageBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def package_tester(log: AxiomLogger, secrets: AxiomSecrets, input: PackageBuildContext) -> PackageBuildContext:
    """Invoke the first published node directly to validate it works in the system."""

    if not input.publish_success:
        input.test_success = False
        input.test_error = f"Cannot test: package publish failed — {input.publish_error}"
        return input

    if not input.node_ids:
        input.test_success = True
        return input

    ingress_url = os.environ.get("INGRESS_URL", "http://axiom-ingress:80")
    axiom_api_key, _ = secrets.get("AXIOM_API_KEY")
    session_id = str(uuid.uuid4()).replace("-", "")
    first_node_id = input.node_ids[0]

    try:
        resp = httpx.post(
            f"{ingress_url}/v1/nodes/{first_node_id}",
            json={},
            headers={
                "Authorization": f"Bearer {axiom_api_key}",
                "X-Debug-Session-Id": session_id,
            },
            timeout=60.0,
        )

        input.session_id = session_id

        if resp.status_code == 200:
            input.test_success = True
        else:
            error_text = resp.text[:500]
            input.test_success = False
            input.test_error = error_text
            if "secret" in error_text.lower():
                input.missing_secrets.append("UNKNOWN_SECRET")
    except Exception as e:
        input.test_success = False
        input.test_error = str(e)
        input.session_id = session_id

    return input
