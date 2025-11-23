"""
eSewa Payment Gateway Integration Utilities (v2 API)
Official Documentation: https://developer.esewa.com.np/pages/Epay
"""
import hmac
import hashlib
import base64
import uuid
import requests
from django.conf import settings


class EsewaPayment:
    """
    eSewa Payment Gateway Integration (v2 API)
    """
    
    # eSewa v2 URLs
    ESEWA_PAYMENT_URL = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"  # Test environment
    ESEWA_VERIFY_URL = "https://rc.esewa.com.np/api/epay/transaction/status/"  # Test verification
    
    # For production, use:
    # ESEWA_PAYMENT_URL = "https://epay.esewa.com.np/api/epay/main/v2/form"
    # ESEWA_VERIFY_URL = "https://epay.esewa.com.np/api/epay/transaction/status/"
    
    def __init__(self):
        # Get eSewa credentials from settings
        self.merchant_id = getattr(settings, 'ESEWA_MERCHANT_ID', 'EPAYTEST')
        self.secret_key = getattr(settings, 'ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
        
    def generate_signature(self, message):
        """
        Generate HMAC SHA256 signature for eSewa v2 API
        
        CRITICAL: According to eSewa v2 documentation:
        - Message format: "total_amount={amount},transaction_uuid={uuid},product_code={code}"
        - All values must be strings WITHOUT decimals (e.g., "100" not "100.0")
        - Must use HMAC-SHA256
        - Must be base64 encoded
        
        Args:
            message: String message to sign
        
        Returns:
            Base64-encoded signature string
        """
        secret = self.secret_key.encode('utf-8')
        message = message.encode('utf-8')
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(secret, message, hashlib.sha256).digest()
        
        # Base64 encode the signature
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return signature_b64
    
    def create_payment_request(self, amount, product_code, total_amount, 
                               success_url, failure_url, transaction_uuid=None):
        """
        Create payment request data for eSewa v2 API
        
        CRITICAL REQUIREMENTS for eSewa v2:
        1. All amount fields must be strings without decimals (e.g., "100" not "100.0")
        2. total_amount MUST equal: amount + tax_amount + product_service_charge + product_delivery_charge
        3. transaction_uuid must be unique for every request (UUID v4 format)
        4. product_code must match merchant panel (use EPAYTEST for testing)
        5. Signature format: "total_amount={total},transaction_uuid={uuid},product_code={code}"
        6. All URLs must be https and publicly accessible (or use test localhost)
        7. signed_field_names must be: "total_amount,transaction_uuid,product_code"
        
        Args:
            amount: Main amount to be paid (product price)
            product_code: Unique identifier (will be overridden to EPAYTEST in test mode)  
            total_amount: Total amount (must equal amount + tax + service + delivery)
            success_url: URL to redirect after successful payment (with query params)
            failure_url: URL to redirect after failed payment
            transaction_uuid: Unique transaction ID (optional, auto-generated if not provided)
        
        Returns:
            dict: Payment request data to send to eSewa v2 API
        """
        # Generate truly unique transaction UUID to avoid 409 conflicts
        if transaction_uuid is None:
            # Use UUID v4 format as per eSewa requirements
            transaction_uuid = str(uuid.uuid4())
        
        # Convert amounts to integers (no decimals) as strings
        # eSewa v2 API expects integer amounts (e.g., "1000" for Rs. 1000)
        amount_int = int(float(amount))
        total_amount_int = int(float(total_amount))
        
        # All additional charges set to 0 (all amounts go to main amount)
        tax_amount = "0"
        product_service_charge = "0"
        product_delivery_charge = "0"
        
        # CRITICAL: Validate total_amount calculation
        # total_amount MUST equal amount + tax + service_charge + delivery_charge
        calculated_total = amount_int + int(tax_amount) + int(product_service_charge) + int(product_delivery_charge)
        if calculated_total != total_amount_int:
            print(f"⚠️  WARNING: total_amount mismatch! Calculated: {calculated_total}, Provided: {total_amount_int}")
            # Fix the total to match calculation
            total_amount_int = calculated_total
        
        # Convert to strings (eSewa expects string format)
        amount_str = str(amount_int)
        total_amount_str = str(total_amount_int)
        
        # CRITICAL: Use merchant_id as product_code for test environment
        # eSewa test environment REQUIRES product_code = "EPAYTEST"
        actual_product_code = self.merchant_id
        
        # Create signature message as per eSewa v2 documentation
        # Format: "total_amount={total},transaction_uuid={uuid},product_code={code}"
        # IMPORTANT: Order matters! Must be exactly as documented
        signature_message = f"total_amount={total_amount_str},transaction_uuid={transaction_uuid},product_code={actual_product_code}"
        
        # Generate HMAC-SHA256 signature
        signature = self.generate_signature(signature_message)
        
        # Debug logging
        print(f"\n=== eSewa v2 Payment Request Debug ===")
        print(f"Amount: {amount_str}")
        print(f"Tax Amount: {tax_amount}")
        print(f"Service Charge: {product_service_charge}")
        print(f"Delivery Charge: {product_delivery_charge}")
        print(f"Total Amount: {total_amount_str}")
        print(f"Transaction UUID: {transaction_uuid}")
        print(f"Product Code: {actual_product_code}")
        print(f"Signature Message: {signature_message}")
        print(f"Signature: {signature}")
        print(f"Success URL: {success_url}")
        print(f"Failure URL: {failure_url}")
        
        # Validate URLs are properly formatted
        if not success_url or not success_url.startswith('http'):
            raise ValueError(f"Invalid success_url: must start with http/https. Got: {success_url}")
        if not failure_url or not failure_url.startswith('http'):
            raise ValueError(f"Invalid failure_url: must start with http/https. Got: {failure_url}")
        
        # Validate success_url contains required query parameters
        if '?' not in success_url:
            print("⚠️  WARNING: success_url should contain query parameters (package_id, payment_amount, etc.)")
        
        # eSewa v2 payment parameters - Order and exact field names matter!
        # MUST match eSewa v2 API specification exactly
        payment_data = {
            'amount': amount_str,
            'tax_amount': tax_amount,
            'total_amount': total_amount_str,
            'transaction_uuid': transaction_uuid,
            'product_code': actual_product_code,
            'product_service_charge': product_service_charge,
            'product_delivery_charge': product_delivery_charge,
            'success_url': success_url,
            'failure_url': failure_url,
            'signed_field_names': 'total_amount,transaction_uuid,product_code',
            'signature': signature
        }
        
        # Comprehensive validation of all required fields
        required_fields = [
            'amount', 'tax_amount', 'total_amount', 'transaction_uuid', 
            'product_code', 'product_service_charge', 'product_delivery_charge',
            'success_url', 'failure_url', 'signature', 'signed_field_names'
        ]
        
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in payment_data:
                missing_fields.append(field)
            elif not str(payment_data[field]).strip():
                empty_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        if empty_fields:
            raise ValueError(f"Empty required fields: {', '.join(empty_fields)}")
        
        # Final validation: ensure total_amount calculation is correct
        total_check = int(amount_str) + int(tax_amount) + int(product_service_charge) + int(product_delivery_charge)
        if total_check != int(total_amount_str):
            raise ValueError(
                f"Invalid total_amount calculation! Expected {total_check} but got {total_amount_str}. "
                f"Formula: amount({amount_str}) + tax({tax_amount}) + service({product_service_charge}) + delivery({product_delivery_charge})"
            )
        
        print(f"\n✅ Payment request created successfully")
        print(f"✅ All {len(payment_data)} required fields validated")
        print(f"✅ Total amount calculation verified: {total_amount_str}\n")
        
        return payment_data
    
    def verify_payment(self, transaction_uuid, total_amount, product_code=None):
        """
        Verify payment with eSewa using status check API
        
        Args:
            transaction_uuid: Transaction UUID from eSewa response
            total_amount: Total amount paid
            product_code: Product code (defaults to merchant_id if not provided)
        
        Returns:
            dict: Verification response with success status
        """
        if product_code is None:
            product_code = self.merchant_id
        
        # Build verification URL with query parameters
        verify_url = f"{self.ESEWA_VERIFY_URL}?product_code={product_code}&total_amount={total_amount}&transaction_uuid={transaction_uuid}"
        
        try:
            response = requests.get(verify_url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # Check if payment status is COMPLETE
            if result.get('status') == 'COMPLETE':
                return {
                    'success': True,
                    'data': result,
                    'transaction_code': result.get('transaction_code'),
                    'message': 'Payment verified successfully'
                }
            else:
                return {
                    'success': False,
                    'data': result,
                    'message': f"Payment status: {result.get('status', 'UNKNOWN')}"
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to verify payment with eSewa'
            }
    
    def decode_payment_response(self, encoded_response):
        """
        Decode Base64-encoded payment response from eSewa
        
        Args:
            encoded_response: Base64-encoded response string from eSewa success callback
        
        Returns:
            dict: Decoded response data containing transaction details
        """
        try:
            decoded_bytes = base64.b64decode(encoded_response)
            decoded_str = decoded_bytes.decode('utf-8')
            
            # Parse the response (it's in query string format)
            params = {}
            for param in decoded_str.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            
            return params
        
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Failed to decode eSewa response'
            }
    
    def get_payment_url(self):
        """Get eSewa payment URL"""
        return self.ESEWA_PAYMENT_URL
    
    def get_verify_url(self):
        """Get eSewa verification URL"""
        return self.ESEWA_VERIFY_URL
