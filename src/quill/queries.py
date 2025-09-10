"""Pydantic models for SQL queries."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ColumnType(str, Enum):
    """SQL column types."""

    INTEGER = "INTEGER"
    TEXT = "TEXT"
    REAL = "REAL"
    BLOB = "BLOB"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"


class ColumnDefinition(BaseModel):
    """Column definition for CREATE TABLE."""

    name: str
    type: ColumnType
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[Any] = None
    auto_increment: bool = False


class CreateTable(BaseModel):
    """CREATE TABLE query model."""

    table_name: str = Field(..., min_length=1)
    columns: List[ColumnDefinition] = Field(..., min_length=1)
    if_not_exists: bool = False

    def to_sql(self) -> str:
        """Generate SQL CREATE TABLE statement."""
        columns_sql = []
        for col in self.columns:
            col_def = f"{col.name} {col.type.value}"
            if col.primary_key:
                col_def += " PRIMARY KEY"
            if col.auto_increment:
                col_def += " AUTOINCREMENT"
            if col.unique and not col.primary_key:
                col_def += " UNIQUE"
            if not col.nullable:
                col_def += " NOT NULL"
            if col.default is not None:
                if isinstance(col.default, str):
                    col_def += f" DEFAULT '{col.default}'"
                else:
                    col_def += f" DEFAULT {col.default}"
            columns_sql.append(col_def)

        columns_str = ", ".join(columns_sql)
        if_not_exists_str = "IF NOT EXISTS " if self.if_not_exists else ""
        return f"CREATE TABLE {if_not_exists_str}{self.table_name} ({columns_str})"


class RenameTable(BaseModel):
    """RENAME TABLE query model."""

    old_name: str = Field(..., min_length=1)
    new_name: str = Field(..., min_length=1)

    def to_sql(self) -> str:
        """Generate SQL ALTER TABLE RENAME statement."""
        return f"ALTER TABLE {self.old_name} RENAME TO {self.new_name}"


class DropTable(BaseModel):
    """DROP TABLE query model."""

    table_name: str = Field(..., min_length=1)
    if_exists: bool = False
    cascade: bool = False

    def to_sql(self) -> str:
        """Generate SQL DROP TABLE statement."""
        if_exists_str = "IF EXISTS " if self.if_exists else ""
        cascade_str = " CASCADE" if self.cascade else ""
        return f"DROP TABLE {if_exists_str}{self.table_name}{cascade_str}"


class Insert(BaseModel):
    """INSERT query model."""

    table_name: str = Field(..., min_length=1)
    values: Dict[str, Any]
    on_conflict: Optional[str] = None  # e.g., "IGNORE", "REPLACE"

    def to_sql(self) -> str:
        """Generate SQL INSERT statement."""
        columns = list(self.values.keys())
        placeholders = ["?" for _ in columns]

        columns_str = ", ".join(columns)
        placeholders_str = ", ".join(placeholders)

        base_sql = (
            f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders_str})"
        )

        if self.on_conflict:
            base_sql = f"INSERT OR {self.on_conflict} INTO {self.table_name} ({columns_str}) VALUES ({placeholders_str})"

        return base_sql

    def get_parameters(self) -> List[Any]:
        """Get parameter values for the prepared statement."""
        return list(self.values.values())


class WhereCondition(BaseModel):
    """WHERE condition for UPDATE, DELETE, SELECT."""

    column: str
    operator: str = "="  # =, !=, <, >, <=, >=, LIKE, IN, etc.
    value: Any

    def to_sql(self) -> str:
        """Convert to SQL WHERE clause part."""
        if self.operator.upper() == "IN" and isinstance(self.value, (list, tuple)):
            placeholders = ", ".join("?" for _ in self.value)
            return f"{self.column} IN ({placeholders})"
        return f"{self.column} {self.operator} ?"

    def get_parameters(self) -> List[Any]:
        """Get parameter values."""
        if self.operator.upper() == "IN" and isinstance(self.value, (list, tuple)):
            return list(self.value)
        return [self.value]


class Update(BaseModel):
    """UPDATE query model."""

    table_name: str = Field(..., min_length=1)
    values: Dict[str, Any] = Field(..., min_length=1)
    where_conditions: List[WhereCondition] = Field(default_factory=list)

    def to_sql(self) -> str:
        """Generate SQL UPDATE statement."""
        set_clauses = [f"{col} = ?" for col in self.values.keys()]
        set_str = ", ".join(set_clauses)

        sql = f"UPDATE {self.table_name} SET {set_str}"

        if self.where_conditions:
            where_clauses = [cond.to_sql() for cond in self.where_conditions]
            where_str = " AND ".join(where_clauses)
            sql += f" WHERE {where_str}"

        return sql

    def get_parameters(self) -> List[Any]:
        """Get parameter values for the prepared statement."""
        params = list(self.values.values())
        for condition in self.where_conditions:
            params.extend(condition.get_parameters())
        return params


class Delete(BaseModel):
    """DELETE query model."""

    table_name: str = Field(..., min_length=1)
    where_conditions: List[WhereCondition] = Field(default_factory=list)

    def to_sql(self) -> str:
        """Generate SQL DELETE statement."""
        sql = f"DELETE FROM {self.table_name}"

        if self.where_conditions:
            where_clauses = [cond.to_sql() for cond in self.where_conditions]
            where_str = " AND ".join(where_clauses)
            sql += f" WHERE {where_str}"

        return sql

    def get_parameters(self) -> List[Any]:
        """Get parameter values for the prepared statement."""
        params = []
        for condition in self.where_conditions:
            params.extend(condition.get_parameters())
        return params


class OrderBy(BaseModel):
    """ORDER BY clause."""

    column: str
    direction: str = "ASC"  # ASC or DESC


class Select(BaseModel):
    """SELECT query model."""

    table_name: str = Field(..., min_length=1)
    columns: List[str] = Field(default_factory=lambda: ["*"])
    where_conditions: List[WhereCondition] = Field(default_factory=list)
    order_by: List[OrderBy] = Field(default_factory=list)
    limit: Optional[int] = None
    offset: Optional[int] = None

    def to_sql(self) -> str:
        """Generate SQL SELECT statement."""
        columns_str = ", ".join(self.columns)
        sql = f"SELECT {columns_str} FROM {self.table_name}"

        if self.where_conditions:
            where_clauses = [cond.to_sql() for cond in self.where_conditions]
            where_str = " AND ".join(where_clauses)
            sql += f" WHERE {where_str}"

        if self.order_by:
            order_clauses = [f"{ob.column} {ob.direction}" for ob in self.order_by]
            order_str = ", ".join(order_clauses)
            sql += f" ORDER BY {order_str}"

        if self.limit is not None:
            sql += f" LIMIT {self.limit}"
            if self.offset is not None:
                sql += f" OFFSET {self.offset}"

        return sql

    def get_parameters(self) -> List[Any]:
        """Get parameter values for the prepared statement."""
        params = []
        for condition in self.where_conditions:
            params.extend(condition.get_parameters())
        return params


# Union type for all query types
Query = Union[CreateTable, RenameTable, DropTable, Insert, Update, Delete, Select]
WriteQuery = Union[CreateTable, RenameTable, DropTable, Insert, Update, Delete]
