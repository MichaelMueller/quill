"""Tests for SQLite database implementation."""

import os
import tempfile

import pytest
import pytest_asyncio

from quill.listener import DatabaseListener
from quill.queries import (
    ColumnDefinition,
    ColumnType,
    CreateTable,
    Delete,
    Insert,
    Select,
    Update,
    WhereCondition,
)
from quill.sqlite import SQLite
from quill.transaction import Transaction


class MockDatabaseListener(DatabaseListener):
    """Mock listener for tracking database events."""

    def __init__(self):
        self.events = []

    async def before_exec(self, query, database):
        self.events.append(f"before_exec: {type(query).__name__}")
        return "before_data"

    async def after_exec(self, query, result, database, before_data=None):
        self.events.append(f"after_exec: {type(query).__name__}")

    async def on_error(self, query, error, database, before_data=None):
        self.events.append(f"error: {type(query).__name__} - {error}")

    async def before_commit(self, database):
        self.events.append("before_commit")
        return "commit_data"

    async def after_commit(self, database, before_data=None):
        self.events.append("after_commit")


@pytest_asyncio.fixture
async def sqlite_db():
    """Create a temporary SQLite database for testing."""
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    db = SQLite(path)
    yield db

    await db.disconnect()
    # Clean up
    if os.path.exists(path):
        os.unlink(path)


@pytest.mark.asyncio
async def test_sqlite_connection():
    """Test SQLite connection and disconnection."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        db = SQLite(path)

        # Initially not connected
        assert db._connection is None

        # Connect
        await db.connect()
        assert db._connection is not None

        # Disconnect
        await db.disconnect()
        assert db._connection is None

    finally:
        if os.path.exists(path):
            os.unlink(path)


@pytest.mark.asyncio
async def test_sqlite_context_manager():
    """Test SQLite as async context manager."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        async with SQLite(path) as db:
            assert db._connection is not None

        assert db._connection is None

    finally:
        if os.path.exists(path):
            os.unlink(path)


@pytest.mark.asyncio
async def test_sqlite_create_and_select(sqlite_db):
    """Test creating a table and selecting from it."""
    # Create table
    columns = [
        ColumnDefinition(name="id", type=ColumnType.INTEGER, primary_key=True),
        ColumnDefinition(name="name", type=ColumnType.TEXT, nullable=False),
        ColumnDefinition(name="email", type=ColumnType.TEXT),
    ]
    create_query = CreateTable(table_name="users", columns=columns)

    result = await sqlite_db.exec(create_query)
    # CREATE TABLE returns rowcount of -1 in SQLite (DDL operations)
    assert result == -1

    # Insert data
    insert_query = Insert(
        table_name="users", values={"name": "John Doe", "email": "john@example.com"}
    )

    result = await sqlite_db.exec(insert_query)
    assert result == 1  # 1 row inserted

    # Select data
    select_query = Select(table_name="users")
    result = await sqlite_db.exec(select_query)

    assert len(result) == 1
    assert result[0]["name"] == "John Doe"
    assert result[0]["email"] == "john@example.com"


@pytest.mark.asyncio
async def test_sqlite_update_and_delete(sqlite_db):
    """Test updating and deleting records."""
    # Setup table and data
    columns = [
        ColumnDefinition(name="id", type=ColumnType.INTEGER, primary_key=True),
        ColumnDefinition(name="name", type=ColumnType.TEXT),
        ColumnDefinition(name="age", type=ColumnType.INTEGER),
    ]
    create_query = CreateTable(table_name="users", columns=columns)
    await sqlite_db.exec(create_query)

    # Insert multiple records
    await sqlite_db.exec(
        Insert(table_name="users", values={"name": "Alice", "age": 25})
    )
    await sqlite_db.exec(Insert(table_name="users", values={"name": "Bob", "age": 30}))

    # Update Alice's age
    update_query = Update(
        table_name="users",
        values={"age": 26},
        where_conditions=[WhereCondition(column="name", value="Alice")],
    )
    result = await sqlite_db.exec(update_query)
    assert result == 1  # 1 row updated

    # Verify update
    select_query = Select(
        table_name="users",
        where_conditions=[WhereCondition(column="name", value="Alice")],
    )
    result = await sqlite_db.exec(select_query)
    assert result[0]["age"] == 26

    # Delete Bob
    delete_query = Delete(
        table_name="users",
        where_conditions=[WhereCondition(column="name", value="Bob")],
    )
    result = await sqlite_db.exec(delete_query)
    assert result == 1  # 1 row deleted

    # Verify only Alice remains
    all_users = await sqlite_db.exec(Select(table_name="users"))
    assert len(all_users) == 1
    assert all_users[0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_sqlite_transaction(sqlite_db):
    """Test executing a transaction."""
    # Setup table
    columns = [
        ColumnDefinition(name="id", type=ColumnType.INTEGER, primary_key=True),
        ColumnDefinition(name="name", type=ColumnType.TEXT),
    ]
    create_query = CreateTable(table_name="users", columns=columns)
    await sqlite_db.exec(create_query)

    # Create transaction with multiple inserts
    transaction = Transaction()
    transaction.insert(Insert(table_name="users", values={"name": "Alice"}))
    transaction.insert(Insert(table_name="users", values={"name": "Bob"}))
    transaction.insert(Insert(table_name="users", values={"name": "Charlie"}))

    # Execute transaction
    results = await sqlite_db.exec(transaction)

    # Should return results for each operation
    assert len(results) == 3
    assert all(result == 1 for result in results)  # Each insert affected 1 row

    # Verify all records were inserted
    all_users = await sqlite_db.exec(Select(table_name="users"))
    assert len(all_users) == 3
    names = {user["name"] for user in all_users}
    assert names == {"Alice", "Bob", "Charlie"}


@pytest.mark.asyncio
async def test_sqlite_listeners(sqlite_db):
    """Test database event listeners."""
    listener = MockDatabaseListener()
    sqlite_db.add_listener(listener)

    # Setup table
    columns = [
        ColumnDefinition(name="id", type=ColumnType.INTEGER, primary_key=True),
        ColumnDefinition(name="name", type=ColumnType.TEXT),
    ]
    create_query = CreateTable(table_name="users", columns=columns)

    # Execute query - should trigger listener events
    await sqlite_db.exec(create_query)

    # Check events were fired
    assert "before_exec: CreateTable" in listener.events
    assert "after_exec: CreateTable" in listener.events

    # Test transaction events
    listener.events.clear()
    transaction = Transaction()
    transaction.insert(Insert(table_name="users", values={"name": "Test"}))

    await sqlite_db.exec(transaction)

    # Should have transaction events and commit events
    assert "before_exec: Transaction" in listener.events
    assert "after_exec: Transaction" in listener.events
    assert "before_commit" in listener.events
    assert "after_commit" in listener.events

    # Test removing listener
    sqlite_db.remove_listener(listener)
    listener.events.clear()

    await sqlite_db.exec(Select(table_name="users"))
    assert len(listener.events) == 0  # No events should be fired
