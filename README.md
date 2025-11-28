# quill
SQL abstraction framework in Python / pydantic.
Realizes the most common sql operations as pydantic models.

# Usage

Sample short example
```python
"""
Quill Framework Showcase with SQLite
=====================================
"""

import sqlite3
from quill import (
    Column, CreateTable, Insert, Select, Update, Delete, 
    Comparison, And, Ref, DropTable
)

def execute_query(conn: sqlite3.Connection, query_obj, description: str):
    """Helper function to execute Quill queries"""
    print(f"\n{description}")
    params = []
    sql = query_obj.to_sql("sqlite", params)
    print(f"SQL: {sql}")
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        
        if isinstance(query_obj, Select):
            results = cursor.fetchall()
            print(f"Results: {results}")
        else:
            print(f"Rows affected: {cursor.rowcount}")
            conn.commit()
    except Exception as e:
        print(f"Error: {e}")

def main():
    conn = sqlite3.connect(":memory:")
    
    # Create table
    users_table = CreateTable(
        table_name="users",
        columns=[
            Column(name="username", data_type="str", max_length=50),
            Column(name="email", data_type="str", max_length=100),
            Column(name="age", data_type="int", is_nullable=True)
        ]
    )
    execute_query(conn, users_table, "Creating users table")
    
    # Insert data
    insert_user = Insert(table_name="users", values={
        "username": "alice", 
        "email": "alice@example.com", 
        "age": 25
    })
    execute_query(conn, insert_user, "Inserting user")
    
    # Select all
    select_all = Select(table_names=["users"])
    execute_query(conn, select_all, "Select all users")
    
    # Select with condition
    select_adult = Select(
        table_names=["users"],
        where=Comparison(operator=">=", left=Ref(name="age"), right=21)
    )
    execute_query(conn, select_adult, "Select adult users")
    
    # Update
    update_age = Update(
        table_name="users",
        values={"age": 26},
        where=Comparison(operator="=", left=Ref(name="username"), right="alice")
    )
    execute_query(conn, update_age, "Update user age")
    
    # Delete
    delete_user = Delete(
        table_name="users",
        where=Comparison(operator="=", left=Ref(name="username"), right="alice")
    )
    execute_query(conn, delete_user, "Delete user")
    
    # Cleanup
    drop_table = DropTable(table_name="users")
    execute_query(conn, drop_table, "Drop table")
    
    conn.close()
    print("\nShowcase completed!")

if __name__ == "__main__":
    main()
```

Sample long example:
```python
"""
Quill Framework Showcase with SQLite
=====================================

This showcase demonstrates the Quill SQL abstraction framework capabilities
using SQLite, including DDL (Data Definition Language) and DML (Data Manipulation Language) operations.
"""

import sqlite3
from typing import Any
from quill import (
    Column, CreateTable, Insert, Select, Update, Delete, 
    Comparison, And, Or, Ref, DropTable, CreateIndex, 
    DropIndex, Transaction
)

def execute_query(conn: sqlite3.Connection, query_obj, description: str):
    """Helper function to execute Quill queries and display results"""
    print(f"\n{description}")
    print("-" * 60)
    
    params = []
    sql = query_obj.to_sql("sqlite", params)
    print(f"Generated SQL: {sql}")
    if params:
        print(f"Parameters: {params}")
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        
        if isinstance(query_obj, Select):
            results = cursor.fetchall()
            if results:
                print(f"Results ({len(results)} rows):")
                for i, row in enumerate(results):
                    print(f"  Row {i+1}: {row}")
            else:
                print("No results returned")
        else:
            print(f"Query executed successfully. Rows affected: {cursor.rowcount}")
            conn.commit()
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback()
    
    print()

def main():
    """Main showcase function"""
    print("=" * 80)
    print("QUILL FRAMEWORK SHOWCASE WITH SQLITE")
    print("=" * 80)
    
    # Connect to SQLite (in-memory database)
    conn = sqlite3.connect(":memory:")
    
    try:
        # ===============================
        # DDL OPERATIONS (Data Definition)
        # ===============================
        
        print("\n🏗️  DDL OPERATIONS (Data Definition Language)")
        print("=" * 80)
        
        # 1. CREATE TABLE - Users
        users_table = CreateTable(
            table_name="users",
            if_not_exists=True,
            columns=[
                Column(name="username", data_type="str", max_length=50),
                Column(name="email", data_type="str", max_length=100),
                Column(name="age", data_type="int", is_nullable=True),
                Column(name="is_active", data_type="bool", default=True),
                Column(name="created_at", data_type="str", default="CURRENT_TIMESTAMP")
            ]
        )
        
        execute_query(conn, users_table, "1. Creating 'users' table")
        
        # 2. CREATE TABLE - Products
        products_table = CreateTable(
            table_name="products",
            columns=[
                Column(name="name", data_type="str", max_length=100),
                Column(name="price", data_type="float"),
                Column(name="in_stock", data_type="bool", default=True),
                Column(name="description", data_type="str", is_nullable=True)
            ]
        )
        
        execute_query(conn, products_table, "2. Creating 'products' table")
        
        # 3. CREATE TABLE - Orders
        orders_table = CreateTable(
            table_name="orders",
            columns=[
                Column(name="user_id", data_type="int"),
                Column(name="product_id", data_type="int"),
                Column(name="quantity", data_type="int", default=1),
                Column(name="order_date", data_type="str", default="CURRENT_DATE")
            ]
        )
        
        execute_query(conn, orders_table, "3. Creating 'orders' table")
        
        # 4. CREATE INDEX
        user_email_index = CreateIndex(
            table_name="users",
            index_name="idx_users_email",
            columns=["email"],
            unique=True
        )
        
        execute_query(conn, user_email_index, "4. Creating unique index on users.email")
        
        # ===============================
        # DML OPERATIONS (Data Manipulation)
        # ===============================
        
        print("\n📊 DML OPERATIONS (Data Manipulation Language)")
        print("=" * 80)
        
        # 1. INSERT operations
        print("\n🔹 INSERT OPERATIONS")
        
        # Insert users
        users_data = [
            {"username": "alice", "email": "alice@example.com", "age": 25},
            {"username": "bob", "email": "bob@example.com", "age": 30},
            {"username": "charlie", "email": "charlie@example.com", "age": None},
            {"username": "diana", "email": "diana@example.com", "age": 28, "is_active": False}
        ]
        
        for i, user_data in enumerate(users_data, 1):
            insert_user = Insert(table_name="users", values=user_data)
            execute_query(conn, insert_user, f"1.{i} Inserting user: {user_data['username']}")
        
        # Insert products
        products_data = [
            {"name": "Laptop", "price": 999.99, "description": "High-performance laptop"},
            {"name": "Mouse", "price": 25.50},
            {"name": "Keyboard", "price": 75.00, "description": "Mechanical keyboard"},
            {"name": "Monitor", "price": 299.99, "in_stock": False}
        ]
        
        for i, product_data in enumerate(products_data, 1):
            insert_product = Insert(table_name="products", values=product_data)
            execute_query(conn, insert_product, f"1.{4+i} Inserting product: {product_data['name']}")
        
        # Insert orders
        orders_data = [
            {"user_id": 1, "product_id": 1, "quantity": 1},
            {"user_id": 1, "product_id": 2, "quantity": 2},
            {"user_id": 2, "product_id": 3, "quantity": 1},
            {"user_id": 3, "product_id": 1, "quantity": 1},
            {"user_id": 2, "product_id": 4, "quantity": 1}
        ]
        
        for i, order_data in enumerate(orders_data, 1):
            insert_order = Insert(table_name="orders", values=order_data)
            execute_query(conn, insert_order, f"1.{8+i} Inserting order: user_id={order_data['user_id']}, product_id={order_data['product_id']}")
        
        # 2. SELECT operations
        print("\n🔹 SELECT OPERATIONS")
        
        # Simple select all
        select_all_users = Select(table_names=["users"])
        execute_query(conn, select_all_users, "2.1 Select all users")
        
        # Select with specific columns
        select_user_info = Select(
            table_names=["users"], 
            columns=["id", "username", "email", "age"]
        )
        execute_query(conn, select_user_info, "2.2 Select user info (specific columns)")
        
        # Select with WHERE condition
        select_active_users = Select(
            table_names=["users"],
            where=Comparison(
                operator="=",
                left=Ref(name="is_active"),
                right=True
            )
        )
        execute_query(conn, select_active_users, "2.3 Select active users only")
        
        # Select with complex WHERE condition (AND)
        select_adult_active_users = Select(
            table_names=["users"],
            where=And(conditions=[
                Comparison(operator="=", left=Ref(name="is_active"), right=True),
                Comparison(operator=">=", left=Ref(name="age"), right=25)
            ])
        )
        execute_query(conn, select_adult_active_users, "2.4 Select active users aged 25+")
        
        # Select with OR condition
        select_young_or_inactive = Select(
            table_names=["users"],
            where=Or(conditions=[
                Comparison(operator="<", left=Ref(name="age"), right=30),
                Comparison(operator="=", left=Ref(name="is_active"), right=False)
            ])
        )
        execute_query(conn, select_young_or_inactive, "2.5 Select users under 30 OR inactive")
        
        # Select with LIKE operator
        select_emails_with_com = Select(
            table_names=["users"],
            columns=["username", "email"],
            where=Comparison(
                operator="LIKE",
                left=Ref(name="email"),
                right="%@example.com"
            )
        )
        execute_query(conn, select_emails_with_com, "2.6 Select users with @example.com emails")
        
        # Select with ORDER BY and LIMIT
        select_top_users = Select(
            table_names=["users"],
            columns=["id", "username", "age"],
            order_by=[("age", "desc"), ("username", "asc")],
            limit=3
        )
        execute_query(conn, select_top_users, "2.7 Select top 3 users ordered by age (desc), then username (asc)")
        
        # Select with JOIN (using multiple tables)
        select_orders_with_users = Select(
            table_names=["orders", "users"],
            columns=["users.username", "orders.quantity", "orders.order_date"],
            where=Comparison(
                operator="=",
                left=Ref(name="orders.user_id"),
                right=Ref(name="users.id")
            )
        )
        execute_query(conn, select_orders_with_users, "2.8 Select orders with user information (JOIN)")
        
        # Select products with price range
        select_affordable_products = Select(
            table_names=["products"],
            where=And(conditions=[
                Comparison(operator=">=", left=Ref(name="price"), right=20.0),
                Comparison(operator="<=", left=Ref(name="price"), right=100.0)
            ])
        )
        execute_query(conn, select_affordable_products, "2.9 Select products in price range $20-$100")
        
        # 3. UPDATE operations
        print("\n🔹 UPDATE OPERATIONS")
        
        # Update single user
        update_user_age = Update(
            table_name="users",
            values={"age": 26},
            where=Comparison(
                operator="=",
                left=Ref(name="username"),
                right="alice"
            )
        )
        execute_query(conn, update_user_age, "3.1 Update Alice's age to 26")
        
        # Update multiple products (price increase)
        update_product_prices = Update(
            table_name="products",
            values={"price": 79.99},
            where=Comparison(
                operator="=",
                left=Ref(name="name"),
                right="Keyboard"
            )
        )
        execute_query(conn, update_product_prices, "3.2 Update keyboard price to $79.99")
        
        # Activate inactive users
        activate_users = Update(
            table_name="users",
            values={"is_active": True},
            where=Comparison(
                operator="=",
                left=Ref(name="is_active"),
                right=False
            )
        )
        execute_query(conn, activate_users, "3.3 Activate all inactive users")
        
        # 4. DELETE operations
        print("\n🔹 DELETE OPERATIONS")
        
        # Delete orders for a specific product
        delete_monitor_orders = Delete(
            table_name="orders",
            where=Comparison(
                operator="=",
                left=Ref(name="product_id"),
                right=4  # Monitor
            )
        )
        execute_query(conn, delete_monitor_orders, "4.1 Delete all orders for monitors")
        
        # Delete products that are out of stock
        delete_out_of_stock = Delete(
            table_name="products",
            where=Comparison(
                operator="=",
                left=Ref(name="in_stock"),
                right=False
            )
        )
        execute_query(conn, delete_out_of_stock, "4.2 Delete out-of-stock products")
        
        # ===============================
        # ADVANCED OPERATIONS
        # ===============================
        
        print("\n🔹 ADVANCED OPERATIONS")
        
        # Show final state of all tables
        final_users = Select(table_names=["users"])
        execute_query(conn, final_users, "Final state: Users table")
        
        final_products = Select(table_names=["products"])
        execute_query(conn, final_products, "Final state: Products table")
        
        final_orders = Select(table_names=["orders"])
        execute_query(conn, final_orders, "Final state: Orders table")
        
        # Complex query: Users with their order counts
        users_with_order_count = Select(
            table_names=["users", "orders"],
            columns=["users.username", "users.email", "COUNT(orders.id) as order_count"],
            where=Comparison(
                operator="=",
                left=Ref(name="users.id"),
                right=Ref(name="orders.user_id")
            )
        )
        # Note: GROUP BY would need to be added to the framework for this to work properly
        # This is just to show the concept
        
        print("\n🔹 CLEANUP OPERATIONS (DDL)")
        
        # Drop index
        drop_email_index = DropIndex(
            table_name="users",
            index_name="idx_users_email"
        )
        execute_query(conn, drop_email_index, "Drop users email index")
        
        # Drop tables (in reverse order of creation due to dependencies)
        for table_name in ["orders", "products", "users"]:
            drop_table = DropTable(table_name=table_name)
            execute_query(conn, drop_table, f"Drop {table_name} table")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        
    print("\n" + "=" * 80)
    print("QUILL FRAMEWORK SHOWCASE COMPLETED!")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("✅ DDL: CREATE TABLE with various column types and constraints")
    print("✅ DDL: CREATE INDEX with unique constraint")
    print("✅ DDL: DROP TABLE and DROP INDEX")
    print("✅ DML: INSERT with various data types")
    print("✅ DML: SELECT with WHERE conditions, ORDER BY, LIMIT")
    print("✅ DML: Complex WHERE conditions using AND, OR")
    print("✅ DML: Comparison operators (=, <, >, >=, LIKE)")
    print("✅ DML: UPDATE with conditions")
    print("✅ DML: DELETE with conditions")
    print("✅ DML: JOIN operations across multiple tables")
    print("✅ Type-safe SQL generation with parameter binding")
    print("✅ Cross-dialect support (demonstrated with SQLite)")

if __name__ == "__main__":
    main()
```