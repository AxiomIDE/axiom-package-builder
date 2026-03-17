import json
import os
import re
import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import PackageSpec, NodeSpec
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert Python developer writing Axiom platform node implementations.
Generate complete, working Python code for each node in the PackageSpec.
Each node file must contain a handle(input, secrets) -> output function.
Each test file must contain at least one pytest test that mocks external dependencies."""


def _to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _generate_node_code(client: anthropic.Anthropic, spec: PackageSpec, node: NodeSpec, fix_instructions: str = "") -> tuple:
    fix_section = f"\n\nFix instructions from previous attempt:\n{fix_instructions}" if fix_instructions else ""

    prompt = f"""Generate Python code for an Axiom node with these specs:

Package: {spec.name}
Node: {node.name}
Description: {node.description}
Input type: {node.input_message}
Output type: {node.output_message}
Node type: {node.node_type} (unary = single request/response)
Required secrets: {list(node.required_secrets)}

Proto definitions (messages.proto):
```proto
{spec.proto_content}
```
{fix_section}

Generate two Python files:

FILE 1: nodes/{_to_snake(node.name)}.py
- Import from gen.axiom_official_axiom_agent_messages_messages_pb2
- Implement handle(input: {node.input_message}, secrets) -> {node.output_message}
- Use secrets.get("MY_SECRET_KEY") for secrets
- Use proper error handling

FILE 2: nodes/test_{_to_snake(node.name)}.py
- Import pytest and unittest.mock
- Test that the module imports and handle function exists
- Mock all external API calls (anthropic, httpx, etc.)

Return as JSON:
{{
  "source_code": "<complete file 1 content>",
  "test_code": "<complete file 2 content>"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    content = message.content[0].text
    if "```json" in content:
        start = content.index("```json") + 7
        end = content.index("```", start)
        content = content[start:end].strip()
    elif "```" in content:
        start = content.index("```") + 3
        end = content.index("```", start)
        content = content[start:end].strip()

    data = json.loads(content)
    return data.get("source_code", ""), data.get("test_code", "")


def code_generator(log: AxiomLogger, secrets: AxiomSecrets, input: PackageSpec) -> PackageSpec:
    api_key = secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    fix_instructions = input.fix_instructions or ""

    for node in input.nodes:
        if node.source_code and not fix_instructions:
            continue

        log.info(f"Generating code for node {node.name}")
        source_code, test_code = _generate_node_code(client, input, node, fix_instructions)
        node.source_code = source_code
        node.test_code = test_code

    input.fix_instructions = ""

    return input
