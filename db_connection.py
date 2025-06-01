"""
Database connection module for the Insurance AI System.
Provides connection pooling and management for PostgreSQL on Railway.com.
"""

import os
import logging
from contextlib import contextmanager
from typing import Generator, Any, Dict

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor, DictCursor, Json
from psycopg2 import sql
import logging
logger = logging.getLogger(__name__)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get database connection details from environment variables
# Railway.com automatically provides these environment variables
DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
DB_NAME = os.environ.get('POSTGRES_DB', 'insurance_ai')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
DB_SCHEMA = os.getenv("DB_SCHEMA", "insurance_ai")

# Connection pool settings
MIN_CONNECTIONS = 1
MAX_CONNECTIONS = 10

# Initialize the connection pool
try:
    connection_pool = SimpleConnectionPool(
        MIN_CONNECTIONS,
        MAX_CONNECTIONS,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    logger.info("Database connection pool initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database connection pool: {e}")
    connection_pool = None


@contextmanager
def get_db_connection() -> Generator[Any, None, None]:
    """
    Context manager for database connections.
    Yields a connection from the pool and ensures it's returned properly.
    """
    connection = None
    try:
        connection = connection_pool.getconn()
        yield connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if connection:
            connection_pool.putconn(connection)


@contextmanager
def get_db_cursor(commit: bool = False) -> Generator[Any, None, None]:
    """
    Context manager for database cursors.
    Yields a cursor and handles commits and rollbacks.
    
    Args:
        commit: Whether to commit the transaction after operations
    """
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            # Set search path to our schema
            cursor.execute(f"SET search_path TO {DB_SCHEMA}, public;")
            yield cursor
            if commit:
                connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error(f"Database operation error: {e}")
            raise
        finally:
            cursor.close()


def execute_query(query: str, params: Dict = None, commit: bool = False) -> list:
    """
    Execute a SQL query and return the results.
    
    Args:
        query: SQL query string
        params: Query parameters
        commit: Whether to commit the transaction
        
    Returns:
        List of query results
    """
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or {})
        if cursor.description:
            return cursor.fetchall()
        return []


def insert_record(table: str, data: Dict, returning: str = "id") -> Dict:
    """
    Insert a record into a table and return the specified column.
    
    Args:
        table: Table name
        data: Dictionary of column names and values
        returning: Column to return after insert
        
    Returns:
        Dictionary containing the returned column value
    """
    columns = list(data.keys())
    values = list(data.values())
    
    # Convert any dict values to JSONB
    for i, value in enumerate(values):
        if isinstance(value, dict):
            values[i] = Json(value)
    
    placeholders = [f'%({col})s' for col in columns]
    
    query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({}) RETURNING {}").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table),
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join(sql.Placeholder(col) for col in columns),
        sql.Identifier(returning)
    )
    
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query.as_string(cursor), data)
        return cursor.fetchone()


def update_record(table: str, id_value: str, data: Dict, id_column: str = "id") -> bool:
    """
    Update a record in a table.
    
    Args:
        table: Table name
        id_value: Value of the ID column
        data: Dictionary of column names and values to update
        id_column: Name of the ID column
        
    Returns:
        True if successful, False otherwise
    """
    if not data:
        return False
    
    # Convert any dict values to JSONB
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = Json(value)
    
    set_items = [f"{col} = %({col})s" for col in data.keys()]
    
    query = sql.SQL("UPDATE {}.{} SET {} WHERE {} = %(id_value)s").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table),
        sql.SQL(', ').join(sql.SQL(f"{col} = %({col})s") for col in data.keys()),
        sql.Identifier(id_column)
    )
    
    params = {**data, "id_value": id_value}
    
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query.as_string(cursor), params)
        return cursor.rowcount > 0


def get_record_by_id(table: str, id_value: str, id_column: str = "id") -> Dict:
    """
    Get a record by its ID.
    
    Args:
        table: Table name
        id_value: Value of the ID column
        id_column: Name of the ID column
        
    Returns:
        Dictionary containing the record data
    """
    params = {}
    query = sql.SQL("SELECT * FROM {}.{} WHERE {} = %(id_value)s").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table),
        sql.Identifier(id_column)
    )
    
    with get_db_cursor() as cursor:
    # Log the SQL query and params before execution
        logger.info(f"Executing query: {query.as_string(cursor)} with params: {params}")

        if not params:
            cursor.execute(query.as_string(cursor))
        else:
            cursor.execute(query.as_string(cursor), params)
            
        return cursor.fetchall()


def get_records(table: str, conditions: Optional[Dict[str, Any]] = None, schema: str = DB_SCHEMA) -> list:
    """Retrieve records from a table based on optional conditions."""
    from psycopg2 import sql

    params = {}
    query_parts = [sql.SQL("SELECT * FROM {}.{}").format(
        sql.Identifier(schema),
        sql.Identifier(table)
    )]

    if conditions:
        where_clauses = []
        for i, (col, val) in enumerate(conditions.items()):
            if val is None:
                continue  # prevent incomplete placeholders
            param_name = f"param_{i}"
            where_clauses.append(sql.SQL("{} = %({})s").format(
                sql.Identifier(col),
                sql.Placeholder(param_name)
            ))
            params[param_name] = val

        if where_clauses:
            query_parts.append(sql.SQL(" WHERE {}").format(
                sql.SQL(" AND ").join(where_clauses)
            ))

    query = sql.SQL("").join(query_parts)

    with get_db_cursor() as cursor:
        logger.info(f"Executing query: {query.as_string(cursor)} with params: {params}")
        if not params:
            cursor.execute(query.as_string(cursor))
        else:
            cursor.execute(query.as_string(cursor), params)
        return cursor.fetchall()


def delete_record(table: str, id_value: str, id_column: str = "id") -> bool:
    """
    Delete a record from a table.
    
    Args:
        table: Table name
        id_value: Value of the ID column
        id_column: Name of the ID column
        
    Returns:
        True if successful, False otherwise
    """
    query = sql.SQL("DELETE FROM {}.{} WHERE {} = %(id_value)s").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table),
        sql.Identifier(id_column)
    )
    
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query.as_string(cursor), {"id_value": id_value})
        return cursor.rowcount > 0


def execute_custom_query(query: str, params: Dict = None, commit: bool = False) -> list:
    """
    Execute a custom SQL query.
    
    Args:
        query: SQL query string
        params: Query parameters
        commit: Whether to commit the transaction
        
    Returns:
        List of query results
    """
    return execute_query(query, params, commit)


def close_all_connections():
    """Close all database connections in the pool."""
    if connection_pool:
        connection_pool.closeall()
        logger.info("All database connections closed")
