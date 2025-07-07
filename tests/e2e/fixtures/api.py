"""
API Client for E2E Tests
"""
import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class APIClient:
    """API client for backend testing"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        
    def request(self, method: str, endpoint: str, 
                data: Optional[Dict] = None,
                params: Optional[Dict] = None) -> requests.Response:
        """Make API request"""
        url = urljoin(self.base_url, endpoint)
        
        response = self.session.request(
            method=method,
            url=url,
            json=data,
            params=params
        )
        
        return response
        
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET request"""
        response = self.request('GET', endpoint, params=params)
        response.raise_for_status()
        return response.json()
        
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """POST request"""
        response = self.request('POST', endpoint, data=data)
        response.raise_for_status()
        return response.json()
        
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """PUT request"""
        response = self.request('PUT', endpoint, data=data)
        response.raise_for_status()
        return response.json()
        
    def delete(self, endpoint: str) -> bool:
        """DELETE request"""
        response = self.request('DELETE', endpoint)
        return response.status_code == 204
        
    def health_check(self) -> bool:
        """Check API health"""
        try:
            response = self.request('GET', '/health')
            return response.status_code == 200
        except:
            return False
            
    def get_papers(self, page: int = 1, limit: int = 10,
                  category: Optional[str] = None) -> Dict:
        """Get papers list"""
        params = {'page': page, 'limit': limit}
        if category:
            params['category'] = category
        return self.get('/api/papers', params=params)
        
    def get_paper(self, paper_id: int) -> Dict:
        """Get single paper"""
        return self.get(f'/api/papers/{paper_id}')
        
    def save_paper(self, paper_id: int) -> Dict:
        """Save paper to reading list"""
        return self.post(f'/api/papers/{paper_id}/save')
        
    def trigger_pipeline(self) -> Dict:
        """Trigger pipeline (admin only)"""
        return self.post('/api/admin/pipeline/trigger')
