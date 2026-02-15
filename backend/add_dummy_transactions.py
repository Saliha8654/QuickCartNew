"""Add dummy transaction histories for demo purposes"""
from models import SessionLocal, TransactionLog
from datetime import datetime, timedelta
import json

def add_dummy_transactions():
    db = SessionLocal()
    
    print("Adding dummy transaction histories...")
    print("=" * 60)
    
    # Transaction 1: Recent successful payment
    transaction1_details = [
        {
            "name": "Colgate Maximum Cavity Protection 75gm",
            "quantity": 2,
            "unit_price": 250.0,
            "total": 500.0
        },
        {
            "name": "Lipton Yellow Label Tea 95gm",
            "quantity": 1,
            "unit_price": 385.0,
            "total": 385.0
        },
        {
            "name": "Kurkure Chutney Chaska 62gm",
            "quantity": 3,
            "unit_price": 50.0,
            "total": 150.0
        }
    ]
    
    transaction1 = TransactionLog(
        details=json.dumps(transaction1_details),
        payment_method="QR Code (EasyPaisa)",
        total_amount=1035.0,  # 500 + 385 + 150
        payment_status="Completed"
    )
    # Manually set timestamp after creation
    transaction1.timestamp = datetime.now() - timedelta(hours=2)
    
    # Transaction 2: Earlier successful payment
    transaction2_details = [
        {
            "name": "Tapal Danedar 95gm",
            "quantity": 2,
            "unit_price": 290.0,
            "total": 580.0
        },
        {
            "name": "Lifebuoy Total Protect Soap 96gm",
            "quantity": 4,
            "unit_price": 85.0,
            "total": 340.0
        },
        {
            "name": "LU Oreo Biscuit 19gm",
            "quantity": 5,
            "unit_price": 30.0,
            "total": 150.0
        },
        {
            "name": "Safeguard Bar Soap Pure White 175gm",
            "quantity": 1,
            "unit_price": 125.0,
            "total": 125.0
        }
    ]
    
    transaction2 = TransactionLog(
        details=json.dumps(transaction2_details),
        payment_method="QR Code (EasyPaisa)",
        total_amount=1195.0,  # 580 + 340 + 150 + 125
        payment_status="Completed"
    )
    # Manually set timestamp after creation
    transaction2.timestamp = datetime.now() - timedelta(days=1, hours=5)
    
    try:
        # Add both transactions
        db.add(transaction1)
        db.add(transaction2)
        db.commit()
        
        print("\n✅ Transaction 1 Added:")
        print(f"   Transaction ID: {transaction1.id}")
        print(f"   Total Amount: PKR {transaction1.total_amount:.2f}")
        print(f"   Payment Method: {transaction1.payment_method}")
        print(f"   Status: {transaction1.payment_status}")
        print(f"   Items: {len(transaction1_details)}")
        print(f"   Timestamp: {transaction1.timestamp}")
        
        print("\n✅ Transaction 2 Added:")
        print(f"   Transaction ID: {transaction2.id}")
        print(f"   Total Amount: PKR {transaction2.total_amount:.2f}")
        print(f"   Payment Method: {transaction2.payment_method}")
        print(f"   Status: {transaction2.payment_status}")
        print(f"   Items: {len(transaction2_details)}")
        print(f"   Timestamp: {transaction2.timestamp}")
        
        print("\n" + "=" * 60)
        print("✅ Successfully added 2 dummy transactions!")
        print("You can now view them in the admin panel at:")
        print("http://localhost:5000/admin/transactions")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error adding transactions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_dummy_transactions()
