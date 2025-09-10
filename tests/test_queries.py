"""Tests for query models."""

import pytest

from quill.queries import (
    ColumnDefinition,
    ColumnType,
    CreateTable,
    Delete,
    DropTable,
    Insert,
    OrderBy,
    RenameTable,
    Select,
    Update,
    WhereCondition,
)


def test_create_table_basic():
    """Test basic CREATE TABLE functionality."""
    columns = [
        ColumnDefinition(name="id", type=ColumnType.INTEGER, primary_key=True),
        ColumnDefinition(name="name", type=ColumnType.TEXT, nullable=False),
        ColumnDefinition(name="age", type=ColumnType.INTEGER),
    ]

    query = CreateTable(table_name="users", columns=columns)
    sql = query.to_sql()

    expected = (
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER)"
    )
    assert sql == expected


def test_create_table_with_options():
    """Test CREATE TABLE with advanced options."""
    columns = [
        ColumnDefinition(
            name="id", type=ColumnType.INTEGER, primary_key=True, auto_increment=True
        ),
        ColumnDefinition(
            name="email", type=ColumnType.TEXT, unique=True, nullable=False
        ),
        ColumnDefinition(name="status", type=ColumnType.TEXT, default="active"),
    ]

    query = CreateTable(table_name="accounts", columns=columns, if_not_exists=True)
    sql = query.to_sql()

    expected = "CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, status TEXT DEFAULT 'active')"
    assert sql == expected


def test_rename_table():
    """Test RENAME TABLE functionality."""
    query = RenameTable(old_name="old_users", new_name="users")
    sql = query.to_sql()

    expected = "ALTER TABLE old_users RENAME TO users"
    assert sql == expected


def test_drop_table():
    """Test DROP TABLE functionality."""
    query = DropTable(table_name="old_table", if_exists=True)
    sql = query.to_sql()

    expected = "DROP TABLE IF EXISTS old_table"
    assert sql == expected


def test_insert():
    """Test INSERT functionality."""
    query = Insert(
        table_name="users",
        values={"name": "John Doe", "age": 30, "email": "john@example.com"},
    )
    sql = query.to_sql()
    params = query.get_parameters()

    expected = "INSERT INTO users (name, age, email) VALUES (?, ?, ?)"
    assert sql == expected
    assert params == ["John Doe", 30, "john@example.com"]


def test_insert_with_conflict():
    """Test INSERT with conflict resolution."""
    query = Insert(
        table_name="users",
        values={"name": "Jane Doe", "email": "jane@example.com"},
        on_conflict="IGNORE",
    )
    sql = query.to_sql()

    expected = "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)"
    assert sql == expected


def test_update():
    """Test UPDATE functionality."""
    conditions = [WhereCondition(column="id", operator="=", value=1)]

    query = Update(
        table_name="users",
        values={"name": "Updated Name", "age": 31},
        where_conditions=conditions,
    )
    sql = query.to_sql()
    params = query.get_parameters()

    expected = "UPDATE users SET name = ?, age = ? WHERE id = ?"
    assert sql == expected
    assert params == ["Updated Name", 31, 1]


def test_delete():
    """Test DELETE functionality."""
    conditions = [
        WhereCondition(column="age", operator=">", value=65),
        WhereCondition(column="status", operator="=", value="inactive"),
    ]

    query = Delete(table_name="users", where_conditions=conditions)
    sql = query.to_sql()
    params = query.get_parameters()

    expected = "DELETE FROM users WHERE age > ? AND status = ?"
    assert sql == expected
    assert params == [65, "inactive"]


def test_select_basic():
    """Test basic SELECT functionality."""
    query = Select(table_name="users")
    sql = query.to_sql()

    expected = "SELECT * FROM users"
    assert sql == expected


def test_select_with_conditions():
    """Test SELECT with WHERE conditions."""
    conditions = [
        WhereCondition(column="age", operator=">=", value=18),
        WhereCondition(column="status", operator="IN", value=["active", "pending"]),
    ]

    order_by = [
        OrderBy(column="name", direction="ASC"),
        OrderBy(column="age", direction="DESC"),
    ]

    query = Select(
        table_name="users",
        columns=["name", "email", "age"],
        where_conditions=conditions,
        order_by=order_by,
        limit=10,
        offset=20,
    )
    sql = query.to_sql()
    params = query.get_parameters()

    expected = "SELECT name, email, age FROM users WHERE age >= ? AND status IN (?, ?) ORDER BY name ASC, age DESC LIMIT 10 OFFSET 20"
    assert sql == expected
    assert params == [18, "active", "pending"]


def test_where_condition_in_operator():
    """Test WHERE condition with IN operator."""
    condition = WhereCondition(
        column="status", operator="IN", value=["active", "pending", "blocked"]
    )
    sql = condition.to_sql()
    params = condition.get_parameters()

    expected = "status IN (?, ?, ?)"
    assert sql == expected
    assert params == ["active", "pending", "blocked"]
