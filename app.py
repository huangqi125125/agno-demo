from agno.agent import Agent
from agno.playground import Playground
from agno.models.azure import AzureOpenAI
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.yfinance import YFinanceTools

search_agent = Agent(
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
    markdown=True,
    instructions=[],
    add_history_to_messages=True,
    tools=[DuckDuckGoTools(), GoogleSearchTools()],
    show_tool_calls=True,
)

finance_agent = Agent(
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
    markdown=True,
    instructions=[],
    add_history_to_messages=True,
    tools=[YFinanceTools()],
    show_tool_calls=True,
)

agent_team = Team(
    mode="coordinate",
    members=[search_agent, finance_agent],
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
    success_criteria="A comprehensive financial news report with clear sections and data-driven insights.",
    instructions=["Always include sources", "use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)
# Print the response on the terminal

playground = Playground(teams=agent_team)
app = playground.get_app()

if __name__ == "__main__":
    playground.serve("playground:app", reload=True)
