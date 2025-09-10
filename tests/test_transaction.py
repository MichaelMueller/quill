"""Tests for Transaction class."""

import pytest

from quill.queries import (
    ColumnDefinition,
    ColumnType,
    CreateTable,
    Delete,
    Insert,
    Update,
    WhereCondition,
)
from quill.transaction import Transaction


def test_transaction_creation():
    """Test creating an empty transaction."""
    transaction = Transaction()

    assert len(transaction) == 0
    assert not transaction
    assert transaction.operations == []


def test_transaction_add_operations():
    """Test adding operations to a transaction."""
    transaction = Transaction()

    # Create table
    columns = [
        ColumnDefinition(name="id", type=ColumnType.INTEGER, primary_key=True),
        ColumnDefinition(name="name", type=ColumnType.TEXT),
    ]
    create_query = CreateTable(table_name="test_table", columns=columns)

    # Insert data
    insert_query = Insert(table_name="test_table", values={"name": "Test User"})

    # Update data
    update_query = Update(
        table_name="test_table",
        values={"name": "Updated User"},
        where_conditions=[WhereCondition(column="id", value=1)],
    )

    # Add operations using fluent interface
    transaction.create_table(create_query).insert(insert_query).update(update_query)

    assert len(transaction) == 3
    assert transaction
    assert len(transaction.operations) == 3


def test_transaction_clear():
    """Test clearing transaction operations."""
    transaction = Transaction()

    columns = [ColumnDefinition(name="id", type=ColumnType.INTEGER)]
    create_query = CreateTable(table_name="test", columns=columns)

    transaction.create_table(create_query)
    assert len(transaction) == 1

    transaction.clear()
    assert len(transaction) == 0
    assert not transaction


def test_transaction_add_operation_generic():
    """Test adding operations using the generic add_operation method."""
    transaction = Transaction()

    insert_query = Insert(
        table_name="users", values={"name": "John", "email": "john@example.com"}
    )

    delete_query = Delete(
        table_name="users", where_conditions=[WhereCondition(column="id", value=1)]
    )

    transaction.add_operation(insert_query).add_operation(delete_query)

    assert len(transaction) == 2
    operations = transaction.operations
    assert isinstance(operations[0], Insert)
    assert isinstance(operations[1], Delete)


def test_transaction_operations_copy():
    """Test that operations property returns a copy."""
    transaction = Transaction()

    insert_query = Insert(table_name="test", values={"name": "test"})
    transaction.insert(insert_query)

    operations = transaction.operations
    operations.clear()  # Modify the returned list

    # Original transaction should still have the operation
    assert len(transaction) == 1
