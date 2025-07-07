#!/usr/bin/env python3
"""Setup test Keycloak realm and users"""
import requests
import json
import time
import sys


def wait_for_keycloak(url, max_retries=30):
    """Wait for Keycloak to be ready"""
    print(f"Waiting for Keycloak at {url}...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health/ready", timeout=5)
            if response.status_code == 200:
                print("Keycloak is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    return False


def get_admin_token(base_url, username, password):
    """Get admin access token"""
    token_url = f"{base_url}/realms/master/protocol/openid-connect/token"
    data = {
        'username': username,
        'password': password,
        'grant_type': 'password',
        'client_id': 'admin-cli'
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Failed to get admin token: {response.status_code}")
        print(response.text)
        return None


def create_realm(base_url, token, realm_name):
    """Create test realm"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    realm_data = {
        'realm': realm_name,
        'enabled': True,
        'sslRequired': 'external',
        'registrationAllowed': False,
        'loginWithEmailAllowed': True,
        'duplicateEmailsAllowed': False,
        'resetPasswordAllowed': True,
        'editUsernameAllowed': False,
        'bruteForceProtected': True
    }
    
    response = requests.post(f"{base_url}/admin/realms", headers=headers, json=realm_data)
    if response.status_code == 201:
        print(f"Realm '{realm_name}' created successfully!")
        return True
    elif response.status_code == 409:
        print(f"Realm '{realm_name}' already exists")
        return True
    else:
        print(f"Failed to create realm: {response.status_code}")
        print(response.text)
        return False


def create_client(base_url, token, realm_name, client_data):
    """Create a client in the realm"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f"{base_url}/admin/realms/{realm_name}/clients", 
        headers=headers, 
        json=client_data
    )
    
    if response.status_code == 201:
        print(f"Client '{client_data['clientId']}' created successfully!")
        # The response might be empty for client creation
        try:
            return response.json() if response.content else {}
        except:
            return {}
    elif response.status_code == 409:
        print(f"Client '{client_data['clientId']}' already exists")
        return None
    else:
        print(f"Failed to create client: {response.status_code}")
        print(response.text)
        return None


def create_user(base_url, token, realm_name, user_data):
    """Create a user in the realm"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f"{base_url}/admin/realms/{realm_name}/users", 
        headers=headers, 
        json=user_data
    )
    
    if response.status_code == 201:
        print(f"User '{user_data['username']}' created successfully!")
        # Get user ID from location header
        location = response.headers.get('Location', '')
        user_id = location.split('/')[-1] if location else None
        return user_id
    elif response.status_code == 409:
        print(f"User '{user_data['username']}' already exists")
        return None
    else:
        print(f"Failed to create user: {response.status_code}")
        print(response.text)
        return None


def main():
    """Setup test Keycloak environment"""
    # Configuration
    KEYCLOAK_URL = "http://localhost:8081"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "test_admin"
    REALM_NAME = "arxiv-test"
    
    # Wait for Keycloak
    if not wait_for_keycloak(KEYCLOAK_URL):
        print("Keycloak failed to start!")
        sys.exit(1)
    
    # Get admin token
    token = get_admin_token(KEYCLOAK_URL, ADMIN_USERNAME, ADMIN_PASSWORD)
    if not token:
        print("Failed to authenticate with Keycloak!")
        sys.exit(1)
    
    # Create realm
    if not create_realm(KEYCLOAK_URL, token, REALM_NAME):
        print("Failed to create realm!")
        sys.exit(1)
    
    # Create frontend client
    frontend_client = {
        'clientId': 'arxiv-frontend',
        'enabled': True,
        'publicClient': True,
        'redirectUris': ['http://localhost:3000/*'],
        'webOrigins': ['http://localhost:3000'],
        'protocol': 'openid-connect',
        'attributes': {
            'pkce.code.challenge.method': 'S256'
        }
    }
    create_client(KEYCLOAK_URL, token, REALM_NAME, frontend_client)
    
    # Create backend client
    backend_client = {
        'clientId': 'arxiv-backend',
        'enabled': True,
        'publicClient': False,
        'serviceAccountsEnabled': True,
        'directAccessGrantsEnabled': True,
        'protocol': 'openid-connect',
        'secret': 'test-client-secret'
    }
    create_client(KEYCLOAK_URL, token, REALM_NAME, backend_client)
    
    # Create test users
    test_users = [
        {
            'username': 'test_admin',
            'email': 'admin@test.com',
            'emailVerified': True,
            'enabled': True,
            'credentials': [{
                'type': 'password',
                'value': 'Test123!',
                'temporary': False
            }]
        },
        {
            'username': 'test_user',
            'email': 'user@test.com',
            'emailVerified': True,
            'enabled': True,
            'credentials': [{
                'type': 'password',
                'value': 'Test123!',
                'temporary': False
            }]
        }
    ]
    
    for user_data in test_users:
        create_user(KEYCLOAK_URL, token, REALM_NAME, user_data)
    
    print("\nTest Keycloak setup complete!")
    print("Test users created:")
    print("  Admin: test_admin / Test123!")
    print("  User:  test_user / Test123!")


if __name__ == "__main__":
    main()
