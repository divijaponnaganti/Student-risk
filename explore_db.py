#!/usr/bin/env python3
"""
Script to explore the database structure
"""

import sqlite3
import os

def explore_database():
    # Connect to the database
    db_path = 'instance/student_support.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    if not tables:
        print("No tables found!")
        return
    
    # Check the first table
    first_table = tables[0][0]
    print(f"\nSchema for table '{first_table}':")
    cursor.execute(f"PRAGMA table_info({first_table});")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  - {column[1]} ({column[2]})")
    
    # Show sample data
    print(f"\nSample data from '{first_table}':")
    cursor.execute(f"SELECT * FROM {first_table} LIMIT 5;")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    explore_database()