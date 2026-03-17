import json
import os

import httpx
import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import PackageBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert at diagnosing errors in Axiom platform node implementations.
Given a test failure and debug events, produce specific fix instructions for the code generator."""


def package_error_analyser(log: AxiomLogger, secrets: AxiomSecrets, input: PackageBuildContext) -> PackageBuildContext:
    if input.test_success:
        input.has_error = False
        input.error_summary = "Tests passed"
        return input

    if input.missing_secrets:
        input.has_error = False
        input.error_summary = f"Tests skipped: missing secrets {list(input.missing_secrets)}"
        return input

    api_key = secrets.get("ANTHROPIC_API_KEY")

    debug_events_text = ""
    if input.session_id:
        ingress_url = os.environ.get("INGRESS_URL", "http://axiom-ingress:80")
        axiom_api_key = secrets.get("AXIOM_API_KEY", "")
        tenant_id = os.environ.get("TENANT_ID", "01AXIOMOFFICIAL000000000000")
        try:
            resp = httpx.get(
                f"{ingress_url}/v1/debug-events",
                params={"session_id": input.session_id, "limit": "50"},
                headers={
                    "Authorization": f"Bearer {axiom_api_key}",
                    "X-Tenant-Id": tenant_id,
                },
                timeout=10.0
            )
            if resp.status_code == 200:
                debug_events_text = json.dumps(resp.json(), indent=2)[:3000]
        except Exception as e:
            log.info(f"Failed to fetch debug events: {e}")

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""A node test failed with this error:
{input.test_error}

Debug events:
{debug_events_text or "(none available)"}

Provide specific fix instructions for the code generator. Be concrete and precise.
What exact changes need to be made to the Python node implementation?"""
        }]
    )

    input.has_error = True
    input.fix_instructions = message.content[0].text
    input.error_summary = (input.test_error or "Unknown error")[:200]
    input.iteration = input.iteration + 1

    return input
