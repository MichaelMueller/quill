# builtin
from typing import Literal
# 3rd party
from pydantic import BaseModel

class SqliteDriverParams(BaseModel):
    database_file: str  # Path to the SQLite database file, may be empty or ":memory:"
    timeout: float = 5.0  # Connection timeout in seconds
    wal_mode: bool = True  # Enable Write-Ahead Logging mode
