"""Abstract Database class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from .queries import Query, Select
from .transaction import Transaction


class Database(ABC):
    """Abstract base class for database implementations."""

    @abstractmethod
    async def exec(self, query: Union[Query, Transaction]) -> Any:
        """Execute a query or transaction.

        Args:
            query: Either a single Query or a Transaction containing multiple operations

        Returns:
            For SELECT queries: List of dictionaries representing rows
            For INSERT/UPDATE/DELETE: Number of affected rows
            For DDL operations (CREATE/DROP/RENAME): None or success indicator
            For Transactions: List of results for each operation
        """
        pass

    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    async def begin_transaction(self) -> None:
        """Begin a database transaction."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        pass
