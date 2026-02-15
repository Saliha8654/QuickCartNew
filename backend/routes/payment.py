from flask import Blueprint, request, jsonify
from models import SessionLocal
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import Stripe
import stripe
from payment_config import get_active_config, validate_config

# Initialize Stripe with secret key from environment
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

payment_bp = Blueprint("payment", __name__)

@payment_bp.get("/payment/config")
def get_payment_config():
    """
    Get merchant configuration for payment processing
    """
    try:
        config = get_active_config()
        is_valid, message = validate_config()
        
        # Don't expose sensitive data like API keys
        safe_config = {
            "merchant_id": config["merchant_id"],
            "account_number": config["account_number"],
            "merchant_name": config["merchant_name"],
            "provider": config["provider"],
            "test_mode": config["test_mode"],
            "is_valid": is_valid,
            "message": message,
            "publishable_key": os.getenv('STRIPE_PUBLISHABLE_KEY')
        }
        
        return jsonify(safe_config)
    except Exception as e:
        return jsonify({
            "error": f"Error fetching payment config: {str(e)}"
        }), 500

@payment_bp.post("/payment/create-payment-intent")
def create_payment_intent():
    """
    Create a Stripe Payment Intent for credit card payments
    """
    try:
        data = request.get_json()
        amount = data.get("amount")  # in cents
        currency = data.get("currency", "pkr").lower()
        order_id = data.get("orderId")
        items = data.get("items", [])
        
        if not amount or not order_id:
            return jsonify({
                "error": "Missing required fields: amount and orderId"
            }), 400
        
        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                "order_id": order_id,
                "integration_check": "accept_a_payment"
            }
        )
        
        return jsonify({
            "clientSecret": intent.client_secret,
            "orderId": order_id
        })
        
    except stripe.error.StripeError as e:
        return jsonify({
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Error creating payment intent: {str(e)}"
        }), 500

@payment_bp.post("/payment/verify")
def verify_payment():
    """
    Verify payment status for Stripe payments
    """
    try:
        data = request.get_json()
        order_id = data.get("orderId")
        amount = data.get("amount")
        payment_intent_id = data.get("paymentIntentId")
        
        if not order_id or not amount:
            return jsonify({
                "success": False,
                "message": "Missing required fields"
            }), 400
            
        # For Stripe, we can verify by retrieving the PaymentIntent
        if payment_intent_id:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == "succeeded":
                return jsonify({
                    "success": True,
                    "message": "Payment verified successfully",
                    "orderId": order_id,
                    "amount": amount,
                    "transactionId": intent.id,
                    "timestamp": intent.created
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"Payment status: {intent.status}"
                })
        else:
            # Fallback verification (demo only)
            return jsonify({
                "success": True,
                "message": "Payment verified successfully",
                "orderId": order_id,
                "amount": amount,
                "transactionId": f"TXN-{order_id.split('-')[-1]}",
                "timestamp": "2023-12-17T10:30:00Z"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error verifying payment: {str(e)}"
        }), 500

@payment_bp.post("/payment/webhook")
def payment_webhook():
    """
    Webhook endpoint for Stripe to notify payment status
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
            )
        except ValueError as e:
            # Invalid payload
            return jsonify({"error": "Invalid payload"}), 400
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return jsonify({"error": "Invalid signature"}), 400

        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            print(f"Payment succeeded: {payment_intent.id}")
            # Update your database here
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            print(f"Payment failed: {payment_intent.id}")
            # Handle failed payment
            
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error processing webhook: {str(e)}"
        }), 500

@payment_bp.get("/payment/status/<order_id>")
def get_payment_status(order_id):
    """
    Get payment status for a specific order
    """
    try:
        # In a real implementation, you would check your database
        # or call Stripe's API to get payment intent status
        
        return jsonify({
            "orderId": order_id,
            "status": "completed",  # Could be: pending, completed, failed, cancelled
            "amount": 1500.00,
            "currency": "PKR",
            "provider": "Stripe",
            "transactionId": f"TXN-{order_id.split('-')[-1]}",
            "timestamp": "2023-12-17T10:30:00Z"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching payment status: {str(e)}"
        }), 500