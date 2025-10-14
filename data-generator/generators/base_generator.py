"""
Base Generator Class
====================

Provides common functionality for all data generators including:
- Database connectivity
- Progress tracking
- Data validation
- Batch processing
- Error handling
"""

import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from tqdm import tqdm

from utils.logger import setup_logger

class BaseGenerator(ABC):
    """Abstract base class for all data generators."""
    
    def __init__(self, config: Dict[str, Any], db_connector):
        """Initialize the base generator with configuration and database connector."""
        self.config = config
        self.db_connector = db_connector
        self.logger = setup_logger(self.__class__.__name__)
        
        # Generation settings
        self.batch_size = config.get('generation', {}).get('batch_size', 10000)
        self.progress_frequency = config.get('generation', {}).get('progress_update_frequency', 5000)
        
        # Output settings
        self.export_csv = config.get('output', {}).get('export_csv', False)
        self.csv_path = config.get('output', {}).get('csv_path', './generated_data/')
        self.compress_csv = config.get('output', {}).get('compress_csv', False)
        self.csv_compression = config.get('output', {}).get('csv_compression', 'gzip')
        self.csv_extension = config.get('output', {}).get('csv_extension', '.csv.gz')
        self.compression_level = config.get('output', {}).get('compression_level', 6)
        self.cleanup_uncompressed = config.get('output', {}).get('cleanup_uncompressed', False)
    
    def insert_data_batch(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """Insert a batch of data into the specified table."""
        if not data:
            return True
            
        try:
            # Convert to pandas DataFrame for easier handling
            df = pd.DataFrame(data)
            
            # Handle data type conversions if needed
            df = self._prepare_dataframe_for_insert(df, table_name)
            
            # Insert into ClickHouse
            success = self.db_connector.insert_dataframe(table_name, df)
            
            if success:
                self.logger.debug(f"✅ Inserted {len(data)} records into {table_name}")
            else:
                self.logger.error(f"❌ Failed to insert batch into {table_name}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error inserting data into {table_name}: {str(e)}")
            return False
    
    def export_to_csv(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """Export generated data to CSV with optional compression."""
        if not self.export_csv or not data:
            return
            
        try:
            import os
            os.makedirs(self.csv_path, exist_ok=True)
            
            df = pd.DataFrame(data)
            
            # Always write to uncompressed CSV first (for batching)
            csv_file = f"{self.csv_path}/{table_name}.csv"
            
            # Append to existing file or create new one
            if os.path.exists(csv_file):
                df.to_csv(csv_file, mode='a', header=False, index=False)
            else:
                df.to_csv(csv_file, index=False)
                
            self.logger.debug(f"📄 Exported {len(data)} records to {csv_file}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not export {table_name} to CSV: {str(e)}")
    
    def finalize_csv_export(self, table_name: str) -> None:
        """Finalize CSV export by compressing if requested."""
        if not self.export_csv or not self.compress_csv:
            return
            
        try:
            import os
            import gzip
            
            csv_file = f"{self.csv_path}/{table_name}.csv"
            compressed_file = f"{self.csv_path}/{table_name}{self.csv_extension}"
            
            if os.path.exists(csv_file):
                # Compress the CSV file
                with open(csv_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb', compresslevel=self.compression_level) as f_out:
                        f_out.write(f_in.read())
                
                # Get file sizes for logging
                original_size = os.path.getsize(csv_file)
                compressed_size = os.path.getsize(compressed_file)
                compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                
                self.logger.info(f"🗜️ Compressed {table_name}.csv: {original_size:,} → {compressed_size:,} bytes ({compression_ratio:.1f}% reduction)")
                
                # Clean up uncompressed file if requested
                if self.cleanup_uncompressed:
                    os.remove(csv_file)
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Could not compress CSV for {table_name}: {str(e)}")
    
    def process_in_batches(self, table_name: str, data_generator, total_records: int) -> bool:
        """Process data generation and insertion in batches with progress tracking."""
        self.logger.info(f"📊 Generating {total_records:,} records for {table_name}")
        
        batch_data = []
        total_inserted = 0
        success = True
        
        # Setup progress bar
        with tqdm(total=total_records, desc=f"Generating {table_name}", unit="records") as pbar:
            
            for i, record in enumerate(data_generator):
                batch_data.append(record)
                
                # Process batch when full
                if len(batch_data) >= self.batch_size:
                    if not self._process_batch(table_name, batch_data):
                        success = False
                        break
                        
                    total_inserted += len(batch_data)
                    pbar.update(len(batch_data))
                    batch_data = []
                
                # Update progress periodically
                if (i + 1) % self.progress_frequency == 0:
                    pbar.set_postfix({"Inserted": f"{total_inserted:,}"})
            
            # Process remaining records
            if batch_data and success:
                if self._process_batch(table_name, batch_data):
                    total_inserted += len(batch_data)
                    pbar.update(len(batch_data))
                else:
                    success = False
        
        if success:
            self.logger.info(f"✅ Successfully generated {total_inserted:,} records for {table_name}")
        else:
            self.logger.error(f"❌ Failed to generate all records for {table_name}")
            
        return success
    
    def _process_batch(self, table_name: str, batch_data: List[Dict[str, Any]]) -> bool:
        """Process a single batch of data (insert + optional CSV export)."""
        # Export to CSV if enabled
        if self.export_csv:
            self.export_to_csv(table_name, batch_data)
        
        # Insert into database
        return self.insert_data_batch(table_name, batch_data)
    
    def _prepare_dataframe_for_insert(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Prepare DataFrame for ClickHouse insertion (handle data types, nulls, etc.)."""
        # Convert Python None to proper null values
        df = df.where(pd.notnull(df), None)
        
        # Handle datetime columns
        datetime_columns = df.select_dtypes(include=['datetime64']).columns
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col])
        
        # Handle boolean columns (ClickHouse expects 0/1)
        bool_columns = df.select_dtypes(include=['bool']).columns
        for col in bool_columns:
            df[col] = df[col].astype(int)
        
        # Handle array columns (convert lists to strings if needed)
        # This depends on how your ClickHouse driver handles arrays
        
        return df
    
    def validate_generated_data(self, table_name: str, expected_count: int) -> bool:
        """Validate that the generated data meets basic quality requirements."""
        try:
            # Check record count
            actual_count = self.db_connector.execute_query(
                f"SELECT COUNT(*) as count FROM {table_name}"
            )[0]['count']
            
            if actual_count != expected_count:
                self.logger.warning(
                    f"⚠️ {table_name}: Expected {expected_count:,} records, got {actual_count:,}"
                )
                return False
            
            # Basic data quality checks
            null_check_query = f"""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(CASE WHEN length(toString(tuple(*))) = 0 THEN 1 ELSE 0 END) as empty_records
                FROM {table_name}
            """
            
            result = self.db_connector.execute_query(null_check_query)[0]
            empty_records = result['empty_records']
            
            if empty_records > 0:
                self.logger.warning(f"⚠️ {table_name}: Found {empty_records} empty records")
                return False
            
            self.logger.info(f"✅ {table_name}: Data validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ {table_name}: Data validation failed - {str(e)}")
            return False
    
    def get_existing_records(self, table_name: str, id_column: str) -> set:
        """Get existing record IDs to avoid duplicates."""
        try:
            query = f"SELECT DISTINCT {id_column} FROM {table_name}"
            results = self.db_connector.execute_query(query)
            return {row[id_column] for row in results}
        except:
            # Table might be empty or not exist yet
            return set()
    
    @abstractmethod
    def generate_table_data(self, table_name: str) -> bool:
        """Generate data for a specific table. Must be implemented by subclasses."""
        pass