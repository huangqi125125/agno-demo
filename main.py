from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.yfinance import YFinanceTools

def main():
    print("Hello from agno-demo!")
    agent = Agent(
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[YFinanceTools(stock_price=True)],
        instructions="Use tables to display data. Don't include any other text.",
        markdown=True,
    )
    agent.print_response("What is the stock price of Apple?", stream=True)


if __name__ == "__main__":
    main()
