import json
import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import AgentRequest, PackageBuildContext, NodeSpec
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert Axiom platform package designer.
Given a user's goal, design a Python Axiom package with the appropriate nodes.
Each node should have a single responsibility and clear input/output types.
Return a JSON object matching the PackageBuildContext structure."""

def intent_classifier(log: AxiomLogger, secrets: AxiomSecrets, input: AgentRequest) -> PackageBuildContext:
    api_key, _ = secrets.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    user_prompt = f"""Design an Axiom package to accomplish this goal:
{input.prompt}

Target language: python

Return a JSON object with these fields:
{{
  "name": "axiom-official/<kebab-case-name>",
  "version": "0.1.0",
  "language": "python",
  "nodes": [
    {{
      "name": "<PascalCase>",
      "input_message": "<PascalCaseInput>",
      "output_message": "<PascalCaseOutput>",
      "node_type": "unary",
      "description": "<what this node does>",
      "required_secrets": []
    }}
  ],
  "proto_content": "<full messages.proto content with all input/output message types>",
  "axiom_yaml": "<full axiom.yaml content>"
}}

Rules:
- Package name must be scoped as axiom-official/<name>
- Every node input/output must be defined in messages.proto
- Keep the package focused on a single domain
- Start with 2-5 nodes maximum"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
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

    ctx = PackageBuildContext(
        name=data.get("name", "axiom-official/new-package"),
        version=data.get("version", "0.1.0"),
        language=data.get("language", "python"),
        proto_content=data.get("proto_content", ""),
        axiom_yaml=data.get("axiom_yaml", ""),
        requirements_txt="anthropic>=0.40.0\nhttpx>=0.28.0\ngrpcio>=1.60.0\ngrpcio-tools>=1.60.0\nprotobuf>=4.25.0\n",
    )

    for nd in data.get("nodes", []):
        ctx.nodes.append(NodeSpec(
            name=nd.get("name", ""),
            input_message=nd.get("input_message", ""),
            output_message=nd.get("output_message", ""),
            node_type=nd.get("node_type", "unary"),
            description=nd.get("description", ""),
            required_secrets=nd.get("required_secrets", []),
        ))

    return ctx
