"""
Keycloak Test Administration Utilities
"""
import requests
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin


class KeycloakTestAdmin:
    """Helper class for Keycloak test operations"""
    
    def __init__(self, server_url: str, admin_username: str, 
                 admin_password: str, realm_name: str):
        self.server_url = server_url
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.realm_name = realm_name
        self.token = None
        self.token_expires = 0
        
    def wait_for_keycloak(self, max_retries: int = 30, delay: int = 2):
        """Wait for Keycloak to be ready"""
        health_url = urljoin(self.server_url, '/health/ready')
        
        for i in range(max_retries):
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    print(f"Keycloak is ready after {i * delay} seconds")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            if i < max_retries - 1:
                time.sleep(delay)
        
        raise TimeoutError("Keycloak failed to start within timeout period")
    
    def get_admin_token(self) -> str:
        """Get admin access token"""
        if self.token and time.time() < self.token_expires:
            return self.token
        
        token_url = urljoin(
            self.server_url, 
            f'/realms/master/protocol/openid-connect/token'
        )
        
        data = {
            'client_id': 'admin-cli',
            'username': self.admin_username,
            'password': self.admin_password,
            'grant_type': 'password'
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.token = token_data['access_token']
        self.token_expires = time.time() + token_data['expires_in'] - 60
        
        return self.token
    
    def create_test_user(self, username: str, password: str, 
                        email: str, roles: List[str]) -> str:
        """Create a test user with specified roles"""
        headers = {
            'Authorization': f'Bearer {self.get_admin_token()}',
            'Content-Type': 'application/json'
        }
        
        # Create user
        user_data = {
            'username': username,
            'email': email,
            'enabled': True,
            'emailVerified': True,
            'credentials': [{
                'type': 'password',
                'value': password,
                'temporary': False
            }]
        }
        
        users_url = urljoin(
            self.server_url,
            f'/admin/realms/{self.realm_name}/users'
        )
        
        response = requests.post(users_url, json=user_data, headers=headers)
        response.raise_for_status()
        
        # Get user ID from location header
        user_id = response.headers['Location'].split('/')[-1]
        
        # Assign roles
        if roles:
            self.assign_roles(user_id, roles)
        
        return user_id
    
    def assign_roles(self, user_id: str, roles: List[str]):
        """Assign roles to user"""
        headers = {
            'Authorization': f'Bearer {self.get_admin_token()}',
            'Content-Type': 'application/json'
        }
        
        # Get available realm roles
        roles_url = urljoin(
            self.server_url,
            f'/admin/realms/{self.realm_name}/roles'
        )
        response = requests.get(roles_url, headers=headers)
        available_roles = {r['name']: r for r in response.json()}
        
        # Map role names to role representations
        role_mappings = []
        for role_name in roles:
            if role_name in available_roles:
                role_mappings.append(available_roles[role_name])
        
        # Assign roles to user
        if role_mappings:
            mapping_url = urljoin(
                self.server_url,
                f'/admin/realms/{self.realm_name}/users/{user_id}/role-mappings/realm'
            )
            requests.post(mapping_url, json=role_mappings, headers=headers)
    
    def delete_user(self, user_id: str):
        """Delete a test user"""
        headers = {
            'Authorization': f'Bearer {self.get_admin_token()}'
        }
        
        delete_url = urljoin(
            self.server_url,
            f'/admin/realms/{self.realm_name}/users/{user_id}'
        )
        
        requests.delete(delete_url, headers=headers)
    
    def get_realm_config(self) -> Dict:
        """Get realm configuration"""
        headers = {
            'Authorization': f'Bearer {self.get_admin_token()}'
        }
        
        realm_url = urljoin(
            self.server_url,
            f'/admin/realms/{self.realm_name}'
        )
        
        response = requests.get(realm_url, headers=headers)
        return response.json()
