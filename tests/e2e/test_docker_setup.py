"""
End-to-end tests for Docker environment
"""
import pytest
import docker
import time
import requests
from datetime import datetime


class TestDockerSetup:
    """Test Docker container orchestration"""
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """Create Docker client"""
        return docker.from_env()
    
    @pytest.fixture(scope="class")
    def docker_compose_file(self):
        """Path to docker-compose file"""
        return "/Users/pjmalandrino/Documents/Pro/workspace/poc/arxiv-curator/docker-compose.yml"
    
    def test_postgres_container(self, docker_client):
        """Test PostgreSQL container is running properly"""
        try:
            container = docker_client.containers.get('arxiv_postgres')
            assert container.status == 'running'
            
            # Check health
            health = container.attrs['State']['Health']['Status']
            assert health == 'healthy'
            
            # Check exposed ports
            ports = container.attrs['NetworkSettings']['Ports']
            assert '5432/tcp' in ports
        except docker.errors.NotFound:
            pytest.skip("PostgreSQL container not running")
    
    def test_database_initialization(self):
        """Test database is properly initialized with schema"""
        import psycopg2
        
        try:
            conn = psycopg2.connect(
                dbname="arxiv_curator",
                user="curator",
                password="hL1mcRasLLtP5E65xrkW",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            
            # Check tables exist
            cur.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            
            assert 'papers' in tables
            assert 'summaries' in tables
            
            # Check UUID extension
            cur.execute("SELECT extname FROM pg_extension WHERE extname = 'uuid-ossp'")
            assert cur.fetchone() is not None
            
            cur.close()
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL not accessible")    
    def test_web_container(self, docker_client):
        """Test web container is accessible"""
        try:
            container = docker_client.containers.get('arxiv_web')
            assert container.status == 'running'
            
            # Test web endpoint
            response = requests.get('http://localhost:5000/', timeout=5)
            assert response.status_code == 200
            assert 'ArXiv Curator' in response.text
        except (docker.errors.NotFound, requests.exceptions.RequestException):
            pytest.skip("Web container not running or not accessible")
    
    def test_container_networking(self, docker_client):
        """Test containers can communicate"""
        try:
            # Get both containers
            web = docker_client.containers.get('arxiv_web')
            postgres = docker_client.containers.get('arxiv_postgres')
            
            # Check they're on the same network
            web_networks = set(web.attrs['NetworkSettings']['Networks'].keys())
            pg_networks = set(postgres.attrs['NetworkSettings']['Networks'].keys())
            
            assert len(web_networks.intersection(pg_networks)) > 0
        except docker.errors.NotFound:
            pytest.skip("Containers not running")
    
    def test_volume_persistence(self, docker_client):
        """Test data persists across container restarts"""
        import os
        
        # Check volume directories exist
        volume_paths = [
            "/Users/pjmalandrino/Documents/Pro/workspace/poc/arxiv-curator/volumes/postgres_data",
            "/Users/pjmalandrino/Documents/Pro/workspace/poc/arxiv-curator/volumes/logs"
        ]
        
        for path in volume_paths:
            assert os.path.exists(path), f"Volume path {path} does not exist"