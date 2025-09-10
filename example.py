#!/usr/bin/env python3
"""Example usage of the Quill SQL abstraction framework."""

import asyncio
import os
import tempfile

from quill import (
    ColumnDefinition,
    ColumnType,
    CreateTable,
    DatabaseListener,
    Delete,
    Insert,
    OrderBy,
    Select,
    SQLite,
    Transaction,
    Update,
    WhereCondition,
)


class ExampleListener(DatabaseListener):
    """Example database listener that logs operations."""

    async def before_exec(self, query, database):
        print(f"🔍 About to execute: {type(query).__name__}")
        return None

    async def after_exec(self, query, result, database, before_data=None):
        print(f"✅ Executed: {type(query).__name__}")

    async def on_error(self, query, error, database, before_data=None):
        print(f"❌ Error in {type(query).__name__}: {error}")

    async def before_commit(self, database):
        print("🔄 About to commit transaction")
        return None

    async def after_commit(self, database, before_data=None):
        print("✅ Transaction committed")


async def main():
    """Demonstrate Quill framework functionality."""
    print("🚀 Quill SQL Abstraction Framework Example\n")

    # Create temporary database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        # Initialize database with listener
        db = SQLite(db_path)
        listener = ExampleListener()
        db.add_listener(listener)

        async with db:
            print("1️⃣  Creating Users Table")
            # Create table using Pydantic model
            create_table = CreateTable(
                table_name="users",
                columns=[
                    ColumnDefinition(
                        name="id",
                        type=ColumnType.INTEGER,
                        primary_key=True,
                        auto_increment=True,
                    ),
                    ColumnDefinition(name="name", type=ColumnType.TEXT, nullable=False),
                    ColumnDefinition(name="email", type=ColumnType.TEXT, unique=True),
                    ColumnDefinition(name="age", type=ColumnType.INTEGER, default=0),
                    ColumnDefinition(
                        name="status",
                        type=ColumnType.TEXT,
                        default="active",
                        nullable=False,
                    ),
                ],
                if_not_exists=True,
            )

            await db.exec(create_table)
            print(f"SQL: {create_table.to_sql()}\n")

            print("2️⃣  Inserting Users")
            # Insert users
            users_data = [
                {"name": "Alice Johnson", "email": "alice@example.com", "age": 28},
                {"name": "Bob Smith", "email": "bob@example.com", "age": 32},
                {"name": "Charlie Brown", "email": "charlie@example.com", "age": 25},
            ]

            for user_data in users_data:
                insert = Insert(table_name="users", values=user_data)
                result = await db.exec(insert)
                print(f"Inserted: {user_data['name']} (affected rows: {result})")

            print()

            print("3️⃣  Querying Users")
            # Select all users
            select_all = Select(table_name="users")
            users = await db.exec(select_all)
            print("All users:")
            for user in users:
                print(
                    f"  - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}, Age: {user['age']}"
                )

            print()

            print("4️⃣  Filtering and Ordering")
            # Select users over 25, ordered by age
            select_filtered = Select(
                table_name="users",
                columns=["name", "email", "age"],
                where_conditions=[WhereCondition(column="age", operator=">", value=25)],
                order_by=[OrderBy(column="age", direction="DESC")],
            )
            filtered_users = await db.exec(select_filtered)
            print("Users over 25 (ordered by age desc):")
            for user in filtered_users:
                print(f"  - {user['name']}: {user['age']} years old")

            print()

            print("5️⃣  Updating Data")
            # Update Bob's age
            update = Update(
                table_name="users",
                values={"age": 33, "status": "updated"},
                where_conditions=[
                    WhereCondition(column="email", value="bob@example.com")
                ],
            )
            affected = await db.exec(update)
            print(f"Updated Bob's age (affected rows: {affected})")

            print()

            print("6️⃣  Using Transactions")
            # Use a transaction to insert multiple records atomically
            transaction = Transaction()
            transaction.insert(
                Insert(
                    table_name="users",
                    values={
                        "name": "David Wilson",
                        "email": "david@example.com",
                        "age": 29,
                    },
                )
            )
            transaction.insert(
                Insert(
                    table_name="users",
                    values={
                        "name": "Emma Davis",
                        "email": "emma@example.com",
                        "age": 26,
                    },
                )
            )
            transaction.update(
                Update(
                    table_name="users",
                    values={"status": "batch_updated"},
                    where_conditions=[
                        WhereCondition(column="age", operator=">=", value=30)
                    ],
                )
            )

            results = await db.exec(transaction)
            print(f"Transaction results: {results}")

            print()

            print("7️⃣  Final User List")
            # Show final state
            final_users = await db.exec(Select(table_name="users"))
            print("Final user list:")
            for user in final_users:
                print(
                    f"  - {user['name']}: {user['age']} years, status: {user['status']}"
                )

            print()

            print("8️⃣  Cleanup - Deleting a User")
            # Delete Charlie
            delete = Delete(
                table_name="users",
                where_conditions=[WhereCondition(column="name", value="Charlie Brown")],
            )
            deleted_count = await db.exec(delete)
            print(f"Deleted {deleted_count} user(s)")

            # Show remaining users
            remaining = await db.exec(Select(table_name="users"))
            print(f"Remaining users: {len(remaining)}")

    finally:
        # Clean up temporary database
        if os.path.exists(db_path):
            os.unlink(db_path)

    print("\n🎉 Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
