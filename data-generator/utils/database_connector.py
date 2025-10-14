"""
ClickHouse Database Connector
=============================

Handles connections and operations with the EuroStyle ClickHouse database.
Provides methods for:
- Connection management
- Data insertion
- Query execution
- Error handling
"""

import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickHouseError

from utils.logger import setup_logger

class ClickHouseConnector:
    """Manages connections and operations with ClickHouse database."""
    
    def __init__(self, db_config: Dict[str, Any]):
        """Initialize the ClickHouse connector with database configuration."""
        self.config = db_config
        self.logger = setup_logger(self.__class__.__name__)
        self.client = None
        
        # Connection parameters
        self.host = db_config.get('host', 'localhost')
        self.port = db_config.get('port', 9002)  # Native port for our EuroStyle container
        self.database = db_config.get('database', 'eurostyle_operational')
        self.username = db_config.get('username', 'eurostyle_user')
        self.password = db_config.get('password', 'eurostyle_demo_2024')
        self.timeout = db_config.get('timeout', 30)
        self.secure = db_config.get('secure', False)
        
        # Initialize connection
        self._connect()
    
    def _connect(self) -> bool:
        """Establish connection to ClickHouse database."""
        try:
            self.client = Client(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                secure=self.secure,
                send_receive_timeout=self.timeout,
                sync_request_timeout=self.timeout,
                compress_block_size=1048576,  # 1MB compression blocks
                settings={
                    'max_execution_time': self.timeout,
                    'send_logs_level': 'warning'
                }
            )
            
            self.logger.debug(f"🔗 Connected to ClickHouse at {self.host}:{self.port}/{self.database}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to ClickHouse: {str(e)}")
            self.client = None
            return False
    
    def test_connection(self) -> bool:
        """Test the database connection with a simple query."""
        try:
            if not self.client:
                return False
                
            result = self.client.execute("SELECT 1 as test")
            return result[0][0] == 1
            
        except Exception as e:
            self.logger.error(f"❌ Connection test failed: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        try:
            if not self.client:
                raise ClickHouseError("No database connection")
            
            # Execute query with column names
            result = self.client.execute(query, params or {}, with_column_types=True)
            
            if not result:
                return []
                
            data, columns = result
            column_names = [col[0] for col in columns]
            
            # Convert to list of dictionaries
            return [dict(zip(column_names, row)) for row in data]
            
        except Exception as e:
            self.logger.error(f"❌ Query execution failed: {str(e)}")
            self.logger.error(f"Query: {query}")
            raise
    
    def execute_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Execute an INSERT/UPDATE/DELETE command."""
        try:
            if not self.client:
                raise ClickHouseError("No database connection")
            
            self.client.execute(command, params or {})
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Command execution failed: {str(e)}")
            self.logger.error(f"Command: {command}")
            return False
    
    def insert_dataframe(self, table_name: str, df: pd.DataFrame) -> bool:
        """Insert a pandas DataFrame into a ClickHouse table."""
        try:
            if not self.client:
                raise ClickHouseError("No database connection")
            
            if df.empty:
                self.logger.warning(f"⚠️ Empty DataFrame for table {table_name}")
                return True
            
            # Convert DataFrame to list of tuples (ClickHouse driver format)
            data = [tuple(row) for row in df.values]
            
            # Get column names
            columns = list(df.columns)
            column_names = ', '.join(columns)
            
            # Use ClickHouse driver's execute method with data parameter
            query = f"INSERT INTO {table_name} ({column_names}) VALUES"
            
            # Execute insert - the driver handles the formatting
            self.client.execute(query, data)
            
            self.logger.debug(f"✅ Inserted {len(df)} records into {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ DataFrame insertion failed for {table_name}: {str(e)}")
            return False
    
    def insert_batch(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """Insert a batch of records (list of dictionaries) into a table."""
        try:
            if not data:
                return True
                
            # Convert to DataFrame and use existing method
            df = pd.DataFrame(data)
            return self.insert_dataframe(table_name, df)
            
        except Exception as e:
            self.logger.error(f"❌ Batch insertion failed for {table_name}: {str(e)}")
            return False
    
    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """Get the schema (column names and types) for a table."""
        try:
            query = f"""
                SELECT name, type 
                FROM system.columns 
                WHERE database = '{self.database}' AND table = '{table_name}'
                ORDER BY position
            """
            
            results = self.execute_query(query)
            return {row['name']: row['type'] for row in results}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get schema for {table_name}: {str(e)}")
            return {}
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            query = f"""
                SELECT COUNT(*) as count
                FROM system.tables
                WHERE database = '{self.database}' AND name = '{table_name}'
            """
            
            result = self.execute_query(query)
            return result[0]['count'] > 0
            
        except Exception as e:
            self.logger.error(f"❌ Error checking table existence for {table_name}: {str(e)}")
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Get the number of records in a table."""
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = self.execute_query(query)
            return result[0]['count']
            
        except Exception as e:
            self.logger.error(f"❌ Error getting count for {table_name}: {str(e)}")
            return -1
    
    def truncate_table(self, table_name: str) -> bool:
        """Truncate a table (remove all data)."""
        try:
            # ClickHouse uses ALTER TABLE ... DELETE WHERE 1=1 for truncate
            command = f"ALTER TABLE {table_name} DELETE WHERE 1=1"
            return self.execute_command(command)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to truncate {table_name}: {str(e)}")
            return False
    
    def optimize_table(self, table_name: str) -> bool:
        """Optimize a table (force merge of parts)."""
        try:
            command = f"OPTIMIZE TABLE {table_name}"
            return self.execute_command(command)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to optimize {table_name}: {str(e)}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database and tables."""
        try:
            # Get all tables
            tables_query = f"""
                SELECT name, engine, total_rows, total_bytes
                FROM system.tables
                WHERE database = '{self.database}'
                ORDER BY name
            """
            
            tables = self.execute_query(tables_query)
            
            # Get database size
            size_query = f"""
                SELECT 
                    sum(total_bytes) as total_size_bytes,
                    sum(total_rows) as total_rows
                FROM system.tables
                WHERE database = '{self.database}'
            """
            
            size_info = self.execute_query(size_query)[0]
            
            return {
                'database': self.database,
                'tables': tables,
                'total_size_bytes': size_info['total_size_bytes'],
                'total_rows': size_info['total_rows'],
                'table_count': len(tables)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get database info: {str(e)}")
            return {}
    
    def close(self) -> None:
        """Close the database connection."""
        if self.client:
            try:
                self.client.disconnect()
                self.logger.debug("🔌 Database connection closed")
            except:
                pass
            finally:
                self.client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor - ensure connection is closed."""
        self.close()