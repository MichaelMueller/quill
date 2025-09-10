# Quill

SQL abstraction framework in Python

## Overview

Quill is a modern SQL abstraction framework that provides:

- **Pydantic Models**: All SQL queries (CREATE TABLE, RENAME TABLE, DROP TABLE, INSERT, UPDATE, DELETE, SELECT) are represented as Pydantic models for easy serialization and validation
- **Transaction Support**: Group multiple operations into atomic transactions
- **Abstract Database Interface**: Extensible design supporting multiple database backends
- **SQLite Implementation**: Full async SQLite support with aiosqlite
- **Database Listeners**: Hook into database operations with before/after execution events
- **Type Safety**: Full type hints and validation throughout

## Quick Start

```python
import asyncio
from quill import SQLite, CreateTable, Insert, Select, ColumnDefinition, ColumnType

async def main():
    # Create database
    async with SQLite(":memory:") as db:
        # Define table schema
        create_table = CreateTable(
            table_name="users",
            columns=[
                ColumnDefinition(name="id", type=ColumnType.INTEGER, primary_key=True),
                ColumnDefinition(name="name", type=ColumnType.TEXT, nullable=False),
                ColumnDefinition(name="email", type=ColumnType.TEXT, unique=True),
            ]
        )
        
        # Execute queries
        await db.exec(create_table)
        await db.exec(Insert(table_name="users", values={"name": "Alice", "email": "alice@example.com"}))
        
        # Query data
        users = await db.exec(Select(table_name="users"))
        print(users)  # [{"id": 1, "name": "Alice", "email": "alice@example.com"}]

asyncio.run(main())
```

## Features

### Pydantic Query Models

All SQL operations are represented as Pydantic models that can be serialized to JSON:

```python
from quill import CreateTable, ColumnDefinition, ColumnType

# Create a table definition
table = CreateTable(
    table_name="products",
    columns=[
        ColumnDefinition(name="id", type=ColumnType.INTEGER, primary_key=True),
        ColumnDefinition(name="name", type=ColumnType.TEXT, nullable=False),
        ColumnDefinition(name="price", type=ColumnType.REAL, default=0.0),
    ]
)

# Serialize to JSON
json_data = table.model_dump_json()

# Generate SQL
sql = table.to_sql()  # "CREATE TABLE products (id INTEGER PRIMARY KEY, ...)"
```

### Transactions

Group multiple operations for atomic execution:

```python
from quill import Transaction, Insert, Update, WhereCondition

transaction = Transaction()
transaction.insert(Insert(table_name="users", values={"name": "Bob"}))
transaction.update(Update(
    table_name="users", 
    values={"status": "active"},
    where_conditions=[WhereCondition(column="name", value="Bob")]
))

results = await db.exec(transaction)
```

### Database Listeners

Hook into database operations:

```python
from quill import DatabaseListener

class LoggingListener(DatabaseListener):
    async def before_exec(self, query, database):
        print(f"Executing: {type(query).__name__}")
    
    async def after_exec(self, query, result, database, before_data=None):
        print(f"Completed: {type(query).__name__}")
    
    async def on_error(self, query, error, database, before_data=None):
        print(f"Error: {error}")
    
    async def before_commit(self, database):
        print("Committing transaction")
    
    async def after_commit(self, database, before_data=None):
        print("Transaction committed")

# Add listener to database
db.add_listener(LoggingListener())
```

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e .[dev]
```

## Development

Run tests:

```bash
pytest
```

Format code:

```bash
black src/ tests/
isort src/ tests/
```

Type checking:

```bash
mypy src/
```

## Architecture

- **`Database`**: Abstract base class for database implementations
- **`SQLite`**: Concrete SQLite implementation with async support
- **`Transaction`**: Container for multiple write operations
- **`DatabaseListener`**: Abstract base class for database event hooks
- **Query Models**: Pydantic models for all SQL operations
  - `CreateTable`, `RenameTable`, `DropTable`
  - `Insert`, `Update`, `Delete`, `Select`
  - Supporting types: `ColumnDefinition`, `WhereCondition`, `OrderBy`

## License

MIT
