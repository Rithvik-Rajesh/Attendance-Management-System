"""
Database Reset Utility

WARNING: This script will DELETE all data from the Attendance database.
Use only for testing or when you need to completely reset the system.

Usage:
    python reset.py
"""

import sqlite3
import sys


def reset_database(db_path='Attendance.db'):
    """
    Drop all tables from the database.
    
    Args:
        db_path: Path to the SQLite database file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        print(f"Connecting to database: {db_path}")
        
        # Get list of all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        
        if not tables:
            print("Database is already empty")
            return True
        
        print(f"Found {len(tables)} table(s) to drop:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Confirm before deleting
        response = input("\nAre you sure you want to delete ALL data? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Reset cancelled")
            return False
        
        # Drop all tables
        for table in tables:
            table_name = table[0]
            try:
                cur.execute(f"DROP TABLE {table_name}")
                print(f"✓ Dropped table: {table_name}")
            except sqlite3.Error as e:
                print(f"✗ Error dropping table {table_name}: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n✓ Database reset complete!")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)