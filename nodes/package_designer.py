import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import PackageBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def package_designer(log: AxiomLogger, secrets: AxiomSecrets, input: PackageBuildContext) -> PackageBuildContext:
    """Search the marketplace for reusable packages, then expand the context
    with full proto definitions and refined node interface contracts."""

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff.default.svc.cluster.local:8083")

    existing_packages = []
    try:
        query = input.name.split("/")[-1].replace("-", " ")
        if input.nodes:
            query += " " + input.nodes[0].description
        resp = httpx.post(
            f"{bff_url}/app/marketplace/search/semantic",
            json={"q": query},
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            existing_packages = data.get("packages", [])[:3]
    except Exception as e:
        log.info(f"Marketplace search failed: {e}")

    if existing_packages:
        similar_context = "\n\nExisting similar packages found in the marketplace:\n"
        for pkg in existing_packages:
            similar_context += f"- {pkg.get('name')}: {pkg.get('description', '')}\n"
        similar_context += "\nConsider importing these instead of rebuilding the same functionality.\n"
        input.fix_instructions = (input.fix_instructions or "") + similar_context

    return input
