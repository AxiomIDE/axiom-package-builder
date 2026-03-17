from gen.axiom_official_axiom_agent_messages_messages_pb2 import AnalysisResult, AgentProgress


def handle(analysis: AnalysisResult, context) -> AgentProgress:
    """Terminal node: convert AnalysisResult to final AgentProgress."""
    if not analysis.has_error:
        return AgentProgress(
            stage="complete",
            message=f"Package built and tested successfully. {analysis.error_summary}",
            complete=True,
            success=True,
        )
    else:
        return AgentProgress(
            stage="error",
            message=f"Build failed after max iterations: {analysis.error_summary}",
            complete=True,
            success=False,
        )
