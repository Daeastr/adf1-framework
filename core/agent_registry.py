AGENT_CAPABILITY_MAP = {
    "CoderAgent": {"FILE_IO", "SECURITY", "SANITIZATION"},
    "ContentAgent": {"QUESTION_ANSWERING"},
    "AnalysisAgent": {"DATA_ANALYSIS"},
    "IntegrationAgent": {"NETWORK", "API_ORCHESTRATION"}
}

def select_agent_for_step(capabilities: list[str]) -> str:
    for agent, supported in AGENT_CAPABILITY_MAP.items():
        if all(cap in supported for cap in capabilities):
            return agent
    return "FallbackAgent"
