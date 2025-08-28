from agno.models.azure import AzureOpenAI
from agno.storage.sqlite import SqliteStorage

db_file = "tmp/data.db"

azure_model = AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3")

session_storage = SqliteStorage(
    table_name="agent_sessions",
    db_file=db_file,
    auto_upgrade_schema=True,
)
