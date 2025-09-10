"""SQLite database implementation."""

from typing import Any, Dict, List, Optional, Union

import aiosqlite

from .database import Database
from .listener import DatabaseListener
from .queries import Query, Select
from .transaction import Transaction


class SQLite(Database):
    """SQLite database implementation with async support."""

    def __init__(self, database_path: str) -> None:
        """Initialize SQLite database.

        Args:
            database_path: Path to the SQLite database file
        """
        self.database_path = database_path
        self._connection: Optional[aiosqlite.Connection] = None
        self._listeners: List[DatabaseListener] = []

    def add_listener(self, listener: DatabaseListener) -> None:
        """Add a database listener for events."""
        self._listeners.append(listener)

    def remove_listener(self, listener: DatabaseListener) -> None:
        """Remove a database listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    async def connect(self) -> None:
        """Establish connection to the SQLite database."""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.database_path)
            self._connection.row_factory = aiosqlite.Row

    async def disconnect(self) -> None:
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def begin_transaction(self) -> None:
        """Begin a database transaction."""
        if not self._connection:
            await self.connect()
        await self._connection.execute("BEGIN")

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._connection:
            # Notify listeners before commit
            before_data_list = []
            for listener in self._listeners:
                before_data = await listener.before_commit(self)
                before_data_list.append(before_data)

            # Perform commit
            await self._connection.commit()

            # Notify listeners after commit
            for i, listener in enumerate(self._listeners):
                await listener.after_commit(self, before_data_list[i])

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._connection:
            await self._connection.rollback()

    async def exec(self, query: Union[Query, Transaction]) -> Any:
        """Execute a query or transaction.

        Args:
            query: Either a single Query or a Transaction containing multiple operations

        Returns:
            For SELECT queries: List of dictionaries representing rows
            For other queries: Number of affected rows or None
            For Transactions: List of results for each operation
        """
        if not self._connection:
            await self.connect()

        # Notify listeners before execution
        before_data_list = []
        for listener in self._listeners:
            try:
                before_data = await listener.before_exec(query, self)
                before_data_list.append(before_data)
            except Exception as e:
                await listener.on_error(query, e, self)
                raise

        try:
            if isinstance(query, Transaction):
                result = await self._exec_transaction(query)
            else:
                result = await self._exec_single_query(query)

            # Notify listeners after successful execution
            for i, listener in enumerate(self._listeners):
                await listener.after_exec(query, result, self, before_data_list[i])

            return result

        except Exception as e:
            # Notify listeners of error
            for i, listener in enumerate(self._listeners):
                await listener.on_error(query, e, self, before_data_list[i])
            raise

    async def _exec_single_query(self, query: Query) -> Any:
        """Execute a single query."""
        sql = query.to_sql()
        params = getattr(query, "get_parameters", lambda: [])()

        cursor = await self._connection.execute(sql, params)

        if isinstance(query, Select):
            # For SELECT queries, return all rows as dictionaries
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            # For other queries, return the number of affected rows
            return cursor.rowcount

    async def _exec_transaction(self, transaction: Transaction) -> List[Any]:
        """Execute all operations in a transaction."""
        results = []

        # Check if we're already in a transaction
        in_transaction = self._connection.in_transaction

        # Begin transaction if not already in one
        if not in_transaction:
            await self.begin_transaction()

        try:
            for operation in transaction.operations:
                result = await self._exec_single_query(operation)
                results.append(result)

            # Only commit if we started the transaction
            if not in_transaction:
                await self.commit()
            return results

        except Exception:
            # Only rollback if we started the transaction
            if not in_transaction:
                await self.rollback()
            raise

    async def __aenter__(self) -> "SQLite":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()
