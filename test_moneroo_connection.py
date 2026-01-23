import os
import requests
import json
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

API_KEY = os.getenv('MONEROO_API_KEY')
API_URL = 'https://api.moneroo.io/v1'

print(f"🔑 Testing Moneroo with Key: {API_KEY[:15]}...")

payload = {
    'amount': 100.0,
    'currency': 'XOF',
    'customer_email': 'test@example.com',
    'customer_phone': '243999999999',
    'order_id': 'TEST_ORDER_12345',
    'order_reference': 'TEST_ORDER_12345',
    'description': 'Test Payment',
    'payment_method': 'mobile_money',
    'return_url': 'http://localhost:8000/payment/callback/',
    'callback_url': 'http://localhost:8000/api/payments/moneroo-callback/',
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

try:
    print("\n🚀 Sending request to Moneroo...")
    response = requests.post(
        f'{API_URL}/payments/initialize',
        json=payload,
        headers=headers,
        timeout=10
    )
    
    print(f"📥 Status Code: {response.status_code}")
    print(f"📄 Response Body: {response.text}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        url = data.get('data', {}).get('payment_url') or data.get('payment_url')
        if url:
            print(f"\n✅ SUCCESS! Redirect URL: {url}")
        else:
            print("\n⚠️  Success response but no URL found.")
    else:
        print("\n❌ FAILED.")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
