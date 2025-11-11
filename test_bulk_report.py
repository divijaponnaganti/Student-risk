#!/usr/bin/env python3
"""
Test script for bulk report functionality
"""

import requests
import json
import sys

def test_bulk_report():
    """Test the bulk report functionality"""
    base_url = "http://localhost:5000"
    
    # Test login as faculty
    login_data = {
        'username': 'F001',
        'password': 'F001',
        'role': 'faculty'
    }
    
    session = requests.Session()
    
    print("Testing bulk report functionality...")
    
    # Login
    try:
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("Login failed")
            return False
            
    except Exception as e:
        print(f"Login error: {e}")
        return False
    
    # Test bulk report generation
    try:
        # Test with High Risk filter
        print("Testing bulk report with High Risk filter...")
        bulk_response = session.get(f"{base_url}/reports/bulk?risk_filter=High Risk")
        print(f"Bulk report status: {bulk_response.status_code}")
        print(f"Content-Type: {bulk_response.headers.get('Content-Type', 'Not specified')}")
        
        if bulk_response.status_code == 200:
            content_type = bulk_response.headers.get('Content-Type', '')
            if 'application/pdf' in content_type:
                print("✅ Bulk report generated successfully (PDF)")
                return True
            else:
                print(f"❌ Unexpected content type: {content_type}")
                print(f"Response preview: {bulk_response.text[:200]}")
                return False
        else:
            print(f"❌ Bulk report failed with status {bulk_response.status_code}")
            print(f"Response: {bulk_response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Bulk report error: {e}")
        return False

if __name__ == "__main__":
    success = test_bulk_report()
    sys.exit(0 if success else 1)