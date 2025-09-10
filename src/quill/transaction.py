"""Transaction class for grouping multiple database operations."""

from typing import List

from .queries import (
    CreateTable,
    Delete,
    DropTable,
    Insert,
    RenameTable,
    Update,
    WriteQuery,
)


class Transaction:
    """A transaction containing multiple write operations."""

    def __init__(self) -> None:
        self._operations: List[WriteQuery] = []

    def create_table(self, query: CreateTable) -> "Transaction":
        """Add a CREATE TABLE operation to the transaction."""
        self._operations.append(query)
        return self

    def rename_table(self, query: RenameTable) -> "Transaction":
        """Add a RENAME TABLE operation to the transaction."""
        self._operations.append(query)
        return self

    def drop_table(self, query: DropTable) -> "Transaction":
        """Add a DROP TABLE operation to the transaction."""
        self._operations.append(query)
        return self

    def insert(self, query: Insert) -> "Transaction":
        """Add an INSERT operation to the transaction."""
        self._operations.append(query)
        return self

    def update(self, query: Update) -> "Transaction":
        """Add an UPDATE operation to the transaction."""
        self._operations.append(query)
        return self

    def delete(self, query: Delete) -> "Transaction":
        """Add a DELETE operation to the transaction."""
        self._operations.append(query)
        return self

    def add_operation(self, query: WriteQuery) -> "Transaction":
        """Add any write operation to the transaction."""
        self._operations.append(query)
        return self

    @property
    def operations(self) -> List[WriteQuery]:
        """Get all operations in the transaction."""
        return self._operations.copy()

    def clear(self) -> "Transaction":
        """Clear all operations from the transaction."""
        self._operations.clear()
        return self

    def __len__(self) -> int:
        """Get the number of operations in the transaction."""
        return len(self._operations)

    def __bool__(self) -> bool:
        """Check if the transaction has any operations."""
        return bool(self._operations)
