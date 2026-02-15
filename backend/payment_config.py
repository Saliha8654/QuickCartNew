"""
Payment Gateway Configuration for Stripe
"""

# ==========================
# MERCHANT ACCOUNT SETTINGS
# ==========================

# Your business/store name
MERCHANT_NAME = "QuickCart Store"

# Choose payment provider: "STRIPE"
PAYMENT_PROVIDER = "STRIPE"

# Stripe Configuration
STRIPE_CONFIG = {
    "merchant_id": "STRIPE_MERCHANT",
    "account_number": "N/A",  # Not applicable for Stripe
    "api_key": "STRIPE_API_KEY_PLACEHOLDER",
    "api_secret": "STRIPE_API_SECRET_PLACEHOLDER",
    "callback_url": "http://localhost:5000/api/payment/webhook",
    "return_url": "http://localhost:3000/receipt",
}

# ==========================
# PAYMENT SETTINGS
# ==========================

# Currency
CURRENCY = "PKR"

# ==========================
# SECURITY SETTINGS
# ==========================

# Enable/Disable test mode (use test credentials)
TEST_MODE = True

# Test credentials (for development only)
TEST_MERCHANT_ID = "QUICKCART-STRIPE-TEST"

# ==========================
# HELPER FUNCTIONS
# ==========================

def get_active_config():
    """Get the active payment provider configuration"""
    if TEST_MODE:
        return {
            "merchant_id": TEST_MERCHANT_ID,
            "account_number": "N/A",
            "merchant_name": MERCHANT_NAME,
            "provider": PAYMENT_PROVIDER,
            "test_mode": True,
        }
    
    return {
        **STRIPE_CONFIG,
        "merchant_name": MERCHANT_NAME,
        "provider": "STRIPE",
        "test_mode": False,
    }

def validate_config():
    """Validate that merchant credentials are configured"""
    config = get_active_config()
    
    if config["test_mode"]:
        return True, "Running in TEST MODE"
    
    # For Stripe, validation happens through the API keys in .env
    import os
    if not os.getenv('STRIPE_PUBLISHABLE_KEY'):
        return False, "Stripe Publishable Key not configured"
    
    if not os.getenv('STRIPE_SECRET_KEY'):
        return False, "Stripe Secret Key not configured"
    
    return True, "Configuration valid"
