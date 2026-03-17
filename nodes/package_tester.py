import logging
import os
import uuid

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import PublishResult, TestResult

logger = logging.getLogger(__name__)


def handle(result: PublishResult, context) -> TestResult:
    """Invoke the first published node directly to validate it works."""

    if not result.success:
        return TestResult(
            success=False,
            error=f"Cannot test: package publish failed — {result.error}",
        )

    if not result.node_ids:
        return TestResult(success=True, output_json="{}")

    ingress_url = os.environ.get("INGRESS_URL", "http://axiom-ingress:80")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")

    session_id = str(uuid.uuid4()).replace("-", "")
    first_node_id = result.node_ids[0]

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

        if resp.status_code == 200:
            return TestResult(
                success=True,
                session_id=session_id,
                output_json=resp.text,
            )
        else:
            error_text = resp.text[:500]
            missing = ["UNKNOWN_SECRET"] if "secret" in error_text.lower() else []
            return TestResult(
                success=False,
                session_id=session_id,
                error=error_text,
                missing_secrets=missing,
            )
    except Exception as e:
        return TestResult(success=False, session_id=session_id, error=str(e))
