import requests

# Test administrator login
login_data = {
    'username': 'admin',
    'password': 'admin@123',
    'role': 'administrator'
}

try:
    response = requests.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
    print(f'Login Response Status: {response.status_code}')
    if 'Location' in response.headers:
        location = response.headers['Location']
        print(f'Redirected to: {location}')
    else:
        print('No redirect, showing response preview:')
        print(response.text[:300])
except Exception as e:
    print(f'Error testing login: {e}')