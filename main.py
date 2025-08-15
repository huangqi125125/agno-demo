from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools


def my_agent():
    print("Hello from agno-demo!")
    my_instructions: list[str] = []
    while True:
        user_input = input("请输入: >> ")
        if user_input.lower() == "exit":
            break
        else:
            agent = Agent(
                model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
                markdown=True,
                instructions=my_instructions,
                add_history_to_messages=True,
                tools=[DuckDuckGoTools()],
            )

            # Print the response on the terminal
            agent.print_response(user_input, stream=True)


if __name__ == "__main__":
    my_agent()
