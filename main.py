from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.yfinance import YFinanceTools
from sentry_sdk.tracing_utils import normalize_incoming_data

model = AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3")


def my_agent():
    print("Hello from agno-demo!")

    while True:
        user_input = input("请输入: >> ")
        if user_input.lower() == "exit":
            break
        else:
            search_agent = Agent(
                model=model,
                markdown=True,
                instructions=[],
                add_history_to_messages=True,
                tools=[DuckDuckGoTools(), GoogleSearchTools()],
                show_tool_calls=True,
            )

            finance_agent = Agent(
                model=model,
                markdown=True,
                instructions=[],
                add_history_to_messages=True,
                tools=[YFinanceTools()],
                show_tool_calls=True,
            )

            agent_team = Team(
                mode="coordinate",
                members=[search_agent],
                model=model,
                success_criteria="A comprehensive financial news report with clear sections and data-driven insights.",
                instructions=["Always include sources", "use tables to display data"],
                show_tool_calls=True,
                markdown=True,
            )
            # Print the response on the terminal
            agent_team.print_response(user_input, stream=True)


if __name__ == "__main__":
    my_agent()
