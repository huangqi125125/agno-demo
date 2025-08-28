from agno.agent import Agent
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.yfinance import YFinanceTools
from common import azure_model, session_storage

search_agent = Agent(
    name="Search Agent",
    model=azure_model,
    markdown=True,
    instructions=[],
    storage=session_storage,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    tools=[DuckDuckGoTools(), GoogleSearchTools()],
    show_tool_calls=True,
)

finance_agent = Agent(
    name="Finance Agent",
    model=azure_model,
    markdown=True,
    instructions=[],
    storage=session_storage,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    tools=[YFinanceTools()],
    show_tool_calls=True,
)

agent_team = Team(
    name="Finance Team",
    mode="coordinate",
    members=[search_agent, finance_agent],
    model=azure_model,
    storage=session_storage,
    success_criteria="A comprehensive financial news report with clear sections and data-driven insights.",
    instructions=["Always include sources", "use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)


def interaction():
    while True:
        user_input = input("请输入: >> ")
        if user_input.lower() == "exit" or user_input.lower() == "q":
            break
        else:
            # Print the response on the terminal
            # agent_team.print_response(user_input, stream=True)
            search_agent.print_response(user_input, stream=True)


if __name__ == "__main__":
    interaction()
