"""
Admin Table Migration Script
Adds the admins table to the database if it doesn't exist
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from models import Base, engine, Admin
from sqlalchemy import inspect

def migrate_admin_table():
    """Create admins table if it doesn't exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'admins' not in existing_tables:
        print("Creating admins table...")
        Base.metadata.create_all(bind=engine, tables=[Admin.__table__])
        print("✅ Admins table created successfully!")
    else:
        print("✓ Admins table already exists")

if __name__ == "__main__":
    print("🔄 Running admin table migration...")
    migrate_admin_table()
    print("✅ Migration complete!")
