"""Database event listener for hooking into database operations."""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from .queries import Query
from .transaction import Transaction


class DatabaseListener(ABC):
    """Abstract base class for database event listeners."""

    @abstractmethod
    async def before_exec(
        self, query: Union[Query, Transaction], database: "Database"
    ) -> Optional[Any]:
        """Called before executing a query or transaction.

        Args:
            query: The query or transaction about to be executed
            database: The database instance executing the query

        Returns:
            Optional data that will be passed to after_exec
        """
        pass

    @abstractmethod
    async def after_exec(
        self,
        query: Union[Query, Transaction],
        result: Any,
        database: "Database",
        before_data: Optional[Any] = None,
    ) -> None:
        """Called after successfully executing a query or transaction.

        Args:
            query: The query or transaction that was executed
            result: The result of the execution
            database: The database instance that executed the query
            before_data: Data returned from before_exec
        """
        pass

    @abstractmethod
    async def on_error(
        self,
        query: Union[Query, Transaction],
        error: Exception,
        database: "Database",
        before_data: Optional[Any] = None,
    ) -> None:
        """Called when an error occurs during query or transaction execution.

        Args:
            query: The query or transaction that failed
            error: The exception that occurred
            database: The database instance that failed to execute the query
            before_data: Data returned from before_exec
        """
        pass

    @abstractmethod
    async def before_commit(self, database: "Database") -> Optional[Any]:
        """Called before committing a transaction.

        Args:
            database: The database instance about to commit

        Returns:
            Optional data that will be passed to after_commit
        """
        pass

    @abstractmethod
    async def after_commit(
        self, database: "Database", before_data: Optional[Any] = None
    ) -> None:
        """Called after successfully committing a transaction.

        Args:
            database: The database instance that committed
            before_data: Data returned from before_commit
        """
        pass
