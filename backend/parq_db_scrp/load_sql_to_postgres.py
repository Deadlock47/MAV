import subprocess
import os
import sys
from pathlib import Path

# PostgreSQL Connection Settings
PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASSWORD = os.getenv('PG_PASSWORD', '1234')
PG_DATABASE = os.getenv('PG_DATABASE', 'freff')
OUTPUT_DIR = "downloads"
# Path to SQL file
SQL_FILE_PATH = "data.sql"  # Update with your SQL file path

# Step 2 — Find .gz files
for file in os.listdir(OUTPUT_DIR):
    if file.endswith(".sql"):

        gz_path = os.path.join(OUTPUT_DIR, file)
        sql_path = os.path.join(OUTPUT_DIR, file.replace(".gz", ""))


        print("Extracted:", gz_path)
        

def run_sql_file(sql_file_path):
    """
    Execute a SQL file using psql command line tool.
    
    Args:
        sql_file_path (str): Path to the SQL file to execute
    
    Returns:
        tuple: (return_code, stdout, stderr)
    """
    print("..........................................")
    sql_file = Path(sql_file_path)
    
    if not sql_file.exists():
        print(f"Error: SQL file not found: {sql_file_path}")
        return 1, "", f"File not found: {sql_file_path}"
    
    # Build psql command
    cmd = [
        r'C:\Program Files\PostgreSQL\18\bin\psql.exe',
        '-U', PG_USER,
        '-d', PG_DATABASE,
        '-f', str(sql_file)
    ]
    
    # Set PGPASSWORD environment variable for password authentication
    env = os.environ.copy()
    env['PGPASSWORD'] = PG_PASSWORD
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

    
cmd = [
     r'C:\Program Files\PostgreSQL\18\bin\psql.exe',
    "-U", "postgres",
    "-d", "freff",
    "-h", "localhost",
    "-p", "5432",
    "-c", "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
]

subprocess.run(cmd)

def run_sql_command(sql_command):
    """
    Execute a SQL command directly.
    
    Args:
        sql_command (str): SQL command to execute
    
    Returns:
        tuple: (return_code, stdout, stderr)
    """
    cmd = [
        r'C:\Program Files\PostgreSQL\18\bin\psql.exe',
        '-U', PG_USER,
        '-d', PG_DATABASE,
        '-f', sql_command
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = PG_PASSWORD
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def load_sql_dump(dump_file_path):
    """
    Load a PostgreSQL dump file into the database.
    
    Args:
        dump_file_path (str): Path to the SQL dump file
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Loading SQL dump from: {dump_file_path}")
    
    return_code, stdout, stderr = run_sql_file(dump_file_path)
    
    if return_code == 0:
        print("✓ SQL dump loaded successfully")
        if stdout:
            print("Output:", stdout)
        return True
    else:
        print("✗ Error loading SQL dump")
        if stderr:
            print("Error:", stderr)
        return False


def execute_query(query):
    """
    Execute a SQL query and return results.
    
    Args:
        query (str): SQL query to execute
    
    Returns:
        str: Query result or error message
    """
    return_code, stdout, stderr = run_sql_command(query)
    
    if return_code == 0:
        return stdout
    else:
        return f"Error: {stderr}"


if __name__ == "__main__":
    # Example usage:
    
    # 1. Load a SQL dump file
    load_sql_dump(gz_path)
    
    # 2. Execute a direct SQL command
    # result = execute_query("SELECT version();")
    # print(result)
    
    # 3. Execute a SQL file
    # return_code, stdout, stderr = run_sql_file(gz_path)
    # if return_code == 0:
    #     print("Success:", stdout)
    # else:
    #     print("Error:", stderr)
    
    print("PostgreSQL SQL Execution Module")
    print("Available functions:")
    print("  - run_sql_file(sql_file_path)")
    print("  - run_sql_command(sql_command)")
    print("  - load_sql_dump(dump_file_path)")
    print("  - execute_query(query)")
