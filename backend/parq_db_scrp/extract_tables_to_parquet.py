"""
Extract all tables from PostgreSQL server and convert to Parquet files
"""
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

# PostgreSQL connection parameters
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "freff"
DB_USER = "postgres"
DB_PASSWORD = "1234"

# Output directory for Parquet files
OUTPUT_DIR = "./jvify/db"

def create_output_directory():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")

def get_all_tables(connection):
    """Fetch all table names from the database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            return tables
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def extract_table_to_parquet(connection, table_name):
    """Extract a single table to Parquet file"""
    try:
        print(f"Extracting table: {table_name}...", end=" ")
        
        # Read table into DataFrame
        df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
        
        # Create output filename
        output_file = os.path.join(OUTPUT_DIR, f"{table_name}.parquet")
        
        # Save to Parquet
        df.to_parquet(output_file, index=False)
        
        print(f"✓ Done ({len(df)} rows)")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main function to extract all tables"""
    try:
        print("="*60)
        print("PostgreSQL to Parquet Extractor")
        print("="*60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Create output directory
        create_output_directory()
        print()
        
        # Connect to PostgreSQL
        print("Connecting to PostgreSQL...")
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("✓ Connected successfully")
        print()
        
        # Get all tables
        tables = get_all_tables(connection)
        print(f"Found {len(tables)} tables:")
        print()
        
        # Extract each table
        successful = 0
        failed = 0
        for table in tables:
            if extract_table_to_parquet(connection, table):
                successful += 1
            else:
                failed += 1
        
        connection.close()
        
        print()
        print("="*60)
        print(f"Extraction Summary:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(tables)}")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
