from gen.axiom_official_axiom_agent_messages_messages_pb2 import AnalysisResult, AgentProgress
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def build_result(log: AxiomLogger, secrets: AxiomSecrets, input: AnalysisResult) -> AgentProgress:
    """Terminal node: convert AnalysisResult to final AgentProgress."""
    if not input.has_error:
        return AgentProgress(
            stage="complete",
            message=f"Package built and tested successfully. {input.error_summary}",
            complete=True,
            success=True,
        )
    else:
        return AgentProgress(
            stage="error",
            message=f"Build failed after max iterations: {input.error_summary}",
            complete=True,
            success=False,
        )
