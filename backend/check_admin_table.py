"""
Check Admin Table in Database
Verifies the admin table structure and shows sample data
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from models import SessionLocal, Admin
from sqlalchemy import inspect

def check_admin_table():
    """Check if admin table exists and show its structure"""
    db = SessionLocal()
    
    try:
        # Check table exists
        from models import engine
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("=" * 60)
        print("DATABASE TABLES")
        print("=" * 60)
        for table in tables:
            print(f"✓ {table}")
        print()
        
        if 'admins' in tables:
            print("=" * 60)
            print("ADMINS TABLE STRUCTURE")
            print("=" * 60)
            columns = inspector.get_columns('admins')
            for col in columns:
                print(f"  {col['name']:20} {str(col['type']):20} {'NOT NULL' if not col['nullable'] else 'NULL'}")
            print()
            
            # Check for existing admins
            admin_count = db.query(Admin).count()
            print("=" * 60)
            print(f"ADMIN USERS COUNT: {admin_count}")
            print("=" * 60)
            
            if admin_count > 0:
                admins = db.query(Admin).all()
                print("\nExisting Admin Users:")
                for admin in admins:
                    print(f"  ID: {admin.id}")
                    print(f"  Email: {admin.email}")
                    print(f"  Username: {admin.username}")
                    print(f"  Created: {admin.created_at}")
                    print(f"  Active: {admin.is_active}")
                    print()
            else:
                print("\n⚠ No admin users found. Create one via the signup page!")
                print("   Navigate to: http://localhost:3000/admin/signup")
            
            print("=" * 60)
            print("✅ Admin table is properly configured!")
            print("=" * 60)
        else:
            print("❌ Admin table not found!")
            
    except Exception as e:
        print(f"❌ Error checking admin table: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_table()
