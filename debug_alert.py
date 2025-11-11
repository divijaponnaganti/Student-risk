import requests
import json
import time

# Test the admin alert functionality with detailed debugging
BASE_URL = "http://localhost:5000"

# Login as admin
print("=== Logging in as admin ===")
session = requests.Session()
login_response = session.post(f"{BASE_URL}/api/login", json={
    "username": "admin",
    "password": "admin@123"
})
print(f"Login status: {login_response.status_code}")
if login_response.status_code == 200:
    print("✓ Admin logged in successfully")
else:
    print("✗ Login failed")
    exit(1)

# Test individual alert to student S001 (User ID 5)
print("\n=== Testing Individual Alert to S001 (User ID 5) ===")

# First, let's see what data the admin_send_alert endpoint is receiving
print("Sending alert with detailed payload...")
alert_response = session.post(f"{BASE_URL}/admin/send_alert/5", json={
    "student_id": "S001",
    "student_name": "John Doe",
    "reason": "Test alert for debugging"
})

print(f"Alert response status: {alert_response.status_code}")
print(f"Alert response content: {alert_response.text}")

# Let's also test with minimal data
print("\n=== Testing with minimal data ===")
minimal_response = session.post(f"{BASE_URL}/admin/send_alert/5", json={
    "student_id": "S001"
})
print(f"Minimal response status: {minimal_response.status_code}")
print(f"Minimal response content: {minimal_response.text}")

# Check the notification log
print("\n=== Checking Notification Log ===")
try:
    with open('data/notification_log.json', 'r') as f:
        log_data = json.load(f)
        print(f"Found {len(log_data)} notifications in log")
        for entry in log_data[-3:]:  # Show last 3 entries
            print(f"  - {entry['timestamp']}: {entry['alert_type']} alert to {entry['student_name']} ({entry['student_id']})")
except FileNotFoundError:
    print("No notification log found")