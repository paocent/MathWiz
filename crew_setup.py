# crew_setup.py
from crewai import Crew
from tools import rag_tool_query, llm_fallback_tool

def build_crew():
    # This registers tools with crewai runtime — actual Crew usage depends on crewai version.
    crew = Crew(
        agents=[],
        tools=[rag_tool_query, llm_fallback_tool],
        verbose=False
    )
    return crew
