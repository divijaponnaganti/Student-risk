import requests
import json

# Simple test to debug the admin_send_alert route
BASE_URL = "http://localhost:5000"

# First, let's test if we can access the admin dashboard directly
print("=== Testing admin dashboard access ===")
try:
    response = requests.get(f"{BASE_URL}/admin/dashboard")
    print(f"Admin dashboard status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Admin dashboard accessible")
    else:
        print(f"✗ Admin dashboard error: {response.text[:200]}")
except Exception as e:
    print(f"✗ Connection error: {e}")

# Test the send_alert endpoint directly without authentication
print("\n=== Testing send_alert endpoint without auth ===")
try:
    response = requests.post(f"{BASE_URL}/admin/send_alert/5", json={
        "student_id": "S001",
        "student_name": "John Doe",
        "reason": "Test alert"
    })
    print(f"Send alert status: {response.status_code}")
    print(f"Send alert response: {response.text}")
except Exception as e:
    print(f"✗ Connection error: {e}")

# Test if Flask is running
print("\n=== Testing Flask server status ===")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Homepage status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Flask server is running")
    else:
        print(f"✗ Homepage error: {response.text[:200]}")
except Exception as e:
    print(f"✗ Connection error: {e}")