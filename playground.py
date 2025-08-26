from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.yfinance import YFinanceTools

agent_storage = SqliteStorage(
    table_name="agent_sessions",
    db_file="tmp/data.db",
)

search_agent = Agent(
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
    markdown=True,
    instructions=[],
    storage=agent_storage,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    tools=[DuckDuckGoTools(), GoogleSearchTools()],
    show_tool_calls=True,
)

finance_agent = Agent(
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
    markdown=True,
    instructions=[],
    storage=agent_storage,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    tools=[YFinanceTools()],
    show_tool_calls=True,
)

playground = Playground(agents=[search_agent, finance_agent])
app = playground.get_app()

if __name__ == "__main__":
    playground.serve("playground:app", port=7777, reload=True)
