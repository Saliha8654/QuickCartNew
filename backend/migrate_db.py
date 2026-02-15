"""
Database Migration Script
Adds new columns to existing tables for both SQLite and MySQL databases
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import config

load_dotenv()

print(f"Connecting to database: {config.DATABASE_URL}")

try:
    # Use SQLAlchemy engine for database operations
    engine = create_engine(config.DATABASE_URL)
    
    with engine.connect() as connection:
        print("✅ Connected to database")
        
        # Check database type
        is_sqlite = config.DATABASE_URL.startswith('sqlite')
        print(f"Database type: {'SQLite' if is_sqlite else 'MySQL'}")
        
        # Check and add columns to products table
        print("\n🔄 Updating products table...")
        
        # Check if columns exist
        if is_sqlite:
            result = connection.execute(text("PRAGMA table_info(products)"))
            columns = {row[1]: row[2] for row in result}  # {name: type}
        else:
            result = connection.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'products'
            """))
            columns = {row[0]: row[1] for row in result}  # {name: type}
        
        # Add inventory column if it doesn't exist
        if 'inventory' not in columns:
            print("  Adding 'inventory' column...")
            if is_sqlite:
                connection.execute(text("ALTER TABLE products ADD COLUMN inventory INTEGER DEFAULT 100"))
            else:
                connection.execute(text("ALTER TABLE products ADD COLUMN inventory INT NOT NULL DEFAULT 100"))
            print("  ✅ Added inventory column")
        else:
            print("  ✓ inventory column already exists")
        
        # Add image_url column if it doesn't exist
        if 'image_url' not in columns:
            print("  Adding 'image_url' column...")
            if is_sqlite:
                connection.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(255)"))
            else:
                connection.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(255) NULL"))
            print("  ✅ Added image_url column")
        else:
            print("  ✓ image_url column already exists")
        
        # Add barcode column if it doesn't exist
        if 'barcode' not in columns:
            print("  Adding 'barcode' column...")
            if is_sqlite:
                # SQLite cannot add UNIQUE constraint to existing table, so we add without UNIQUE first
                connection.execute(text("ALTER TABLE products ADD COLUMN barcode VARCHAR(32)"))
            else:
                connection.execute(text("ALTER TABLE products ADD COLUMN barcode VARCHAR(32) UNIQUE NULL"))
            print("  ✅ Added barcode column")
        else:
            print("  ✓ barcode column already exists")
        
        # Check and add columns to cart table
        print("\n🔄 Updating cart table...")
        
        if is_sqlite:
            result = connection.execute(text("PRAGMA table_info(cart)"))
            columns = {row[1]: row[2] for row in result}
        else:
            result = connection.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'cart'
            """))
            columns = {row[0]: row[1] for row in result}
        
        if 'weight_verified' not in columns:
            print("  Adding 'weight_verified' column...")
            if is_sqlite:
                connection.execute(text("ALTER TABLE cart ADD COLUMN weight_verified INTEGER DEFAULT 0"))
            else:
                connection.execute(text("ALTER TABLE cart ADD COLUMN weight_verified INT DEFAULT 0"))
            print("  ✅ Added weight_verified column")
        else:
            print("  ✓ weight_verified column already exists")
        
        # Check and add columns to transactions table
        print("\n🔄 Updating transactions table...")
        
        if is_sqlite:
            result = connection.execute(text("PRAGMA table_info(transactions)"))
            columns = {row[1]: row[2] for row in result}
        else:
            result = connection.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'transactions'
            """))
            columns = {row[0]: row[1] for row in result}
        
        if 'total_amount' not in columns:
            print("  Adding 'total_amount' column...")
            if is_sqlite:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN total_amount REAL DEFAULT 0.0"))
            else:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN total_amount FLOAT NOT NULL DEFAULT 0.0"))
            print("  ✅ Added total_amount column")
        else:
            print("  ✓ total_amount column already exists")
        
        if 'payment_method' not in columns:
            print("  Adding 'payment_method' column...")
            if is_sqlite:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN payment_method VARCHAR(50)"))
            else:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN payment_method VARCHAR(50) NULL"))
            print("  ✅ Added payment_method column")
        else:
            print("  ✓ payment_method column already exists")
        
        if 'payment_status' not in columns:
            print("  Adding 'payment_status' column...")
            if is_sqlite:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN payment_status VARCHAR(50) DEFAULT 'pending'"))
            else:
                connection.execute(text("ALTER TABLE transactions ADD COLUMN payment_status VARCHAR(50) DEFAULT 'pending'"))
            print("  ✅ Added payment_status column")
        else:
            print("  ✓ payment_status column already exists")
        
        # Commit changes
        connection.commit()
        
        print("\n" + "="*50)
        print("✅ Database migration completed successfully!")
        print("="*50)

except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()