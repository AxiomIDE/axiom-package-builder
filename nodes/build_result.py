from gen.axiom_official_axiom_agent_messages_messages_pb2 import PackageBuildContext, AgentProgress
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def build_result(log: AxiomLogger, secrets: AxiomSecrets, input: PackageBuildContext) -> AgentProgress:
    """Terminal node: convert final PackageBuildContext to AgentProgress."""
    if not input.has_error and input.publish_success:
        return AgentProgress(
            stage="complete",
            message=f"Package {input.name} built and tested successfully.",
            complete=True,
            success=True,
            package_name=input.name,
        )
    elif not input.has_error and input.missing_secrets:
        return AgentProgress(
            stage="complete",
            message=f"Package {input.name} published but system tests skipped: {input.error_summary}",
            complete=True,
            success=True,
            package_name=input.name,
        )
    else:
        return AgentProgress(
            stage="error",
            message=f"Build failed after {input.iteration} iteration(s): {input.error_summary}",
            complete=True,
            success=False,
        )
