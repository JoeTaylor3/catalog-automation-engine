"""
Database manager for catalog-automation-engine.
Provides methods to load CSV data into SQLite, create tables dynamically, and execute structured queries.
"""

import sqlite3
import pandas as pd
from pathlib import Path


class DBManager:
    """Manages SQLite database for catalog data with dynamic schema creation and querying."""

    def __init__(self, db_path=None):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. Defaults to 'catalog.db' in current dir.
        """
        self.db_path = db_path or "catalog.db"
        self.connection = None
        self.table_name = "products"

    def connect(self):
        """Establish connection to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Allow dict-like access
            print(f"Connected to SQLite database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print(f"Disconnected from database: {self.db_path}")

    def load_csv(self, csv_path):
        """Load CSV file into SQLite database.
        
        Creates table dynamically based on CSV structure and inserts all records.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            int: Number of records inserted
        """
        if not self.connection:
            self.connect()

        # Read CSV with pandas
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} records from {csv_path}")

        # Create table dynamically based on dataframe structure
        self._create_table(df)

        # Insert records
        df.to_sql(self.table_name, self.connection, if_exists="append", index=False)
        self.connection.commit()
        print(f"Inserted {len(df)} records into table '{self.table_name}'")

        return len(df)

    def _create_table(self, df):
        """Create table dynamically from dataframe structure.
        
        Args:
            df: pandas DataFrame to infer schema from
        """
        # Map pandas dtypes to SQLite types
        type_map = {
            "object": "TEXT",
            "int64": "INTEGER",
            "float64": "REAL",
            "bool": "INTEGER",
        }

        # Build CREATE TABLE statement with auto-increment id and allow duplicate SKUs
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for col, dtype in df.dtypes.items():
            sql_type = type_map.get(str(dtype), "TEXT")
            columns.append(f"{col} {sql_type}")

        create_stmt = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(columns)})"

        try:
            self.connection.execute(create_stmt)
            self.connection.commit()
            print(f"Created table '{self.table_name}' with {len(columns)} columns")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            raise

    def detect_duplicate_skus(self):
        """Detect duplicate SKUs in the catalog.
        
        Returns:
            list: List of dicts with sku and occurrence_count
        """
        if not self.connection:
            self.connect()

        query = f"""
        SELECT sku, COUNT(*) as occurrence_count
        FROM {self.table_name}
        GROUP BY sku
        HAVING COUNT(*) > 1
        ORDER BY occurrence_count DESC
        """

        cursor = self.connection.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        return results

    def count_records_by_category(self):
        """Count records grouped by category.
        
        Returns:
            list: List of dicts with category and record_count
        """
        if not self.connection:
            self.connect()

        query = f"""
        SELECT category, COUNT(*) as record_count
        FROM {self.table_name}
        GROUP BY category
        ORDER BY record_count DESC
        """

        cursor = self.connection.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        return results

    def find_high_price_products(self, threshold=5000):
        """Find products with price above threshold.
        
        Args:
            threshold: Price threshold (default 5000)
            
        Returns:
            list: List of dicts with sku, product_name, price
        """
        if not self.connection:
            self.connect()

        query = f"""
        SELECT sku, product_name, price
        FROM {self.table_name}
        WHERE price > ?
        ORDER BY price DESC
        """

        cursor = self.connection.execute(query, (threshold,))
        results = [dict(row) for row in cursor.fetchall()]
        return results

    def calculate_inventory_by_category(self):
        """Calculate total inventory grouped by category.
        
        Returns:
            list: List of dicts with category and total_inventory
        """
        if not self.connection:
            self.connect()

        query = f"""
        SELECT category, SUM(inventory_count) as total_inventory
        FROM {self.table_name}
        GROUP BY category
        ORDER BY total_inventory DESC
        """

        cursor = self.connection.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        return results

    def execute_query(self, sql, params=None):
        """Execute arbitrary SQL query and return results as list of dicts.
        
        Args:
            sql: SQL query string
            params: Query parameters (tuple or list)
            
        Returns:
            list: List of dicts representing query results
        """
        if not self.connection:
            self.connect()

        try:
            if params:
                cursor = self.connection.execute(sql, params)
            else:
                cursor = self.connection.execute(sql)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            raise
