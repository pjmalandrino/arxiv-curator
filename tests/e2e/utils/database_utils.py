"""
Database Helper Utilities
"""
import asyncpg
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import asyncio


class DatabaseHelper:
    """Database helper for E2E tests using asyncpg"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
        
    async def connect(self):
        """Establish database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=5
            )
            
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            
    async def execute(self, query: str, *args) -> List[Dict]:
        """Execute query and return results"""
        await self.connect()
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]
            
    async def create_papers(self, papers: List[Dict]) -> List[int]:
        """Create test papers"""
        created_ids = []
        await self.connect()
        
        async with self.pool.acquire() as connection:
            for paper in papers:
                query = """
                    INSERT INTO papers (
                        arxiv_id, title, authors, abstract, 
                        categories, created_at, summary
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id
                """
                
                row = await connection.fetchrow(
                    query,
                    paper['arxiv_id'],
                    paper['title'],
                    json.dumps(paper['authors']),
                    paper['abstract'],
                    json.dumps(paper['categories']),
                    paper.get('created_at', datetime.now()),
                    paper.get('summary', '')
                )
                
                if row:
                    created_ids.append(row['id'])
                    
        return created_ids
        
    async def delete_papers(self, paper_ids: List[int]):
        """Delete test papers"""
        if paper_ids:
            await self.connect()
            async with self.pool.acquire() as connection:
                query = "DELETE FROM papers WHERE id = ANY($1::int[])"
                await connection.execute(query, paper_ids)
            
    async def create_user_preference(self, user_id: str, preferences: Dict) -> int:
        """Create user preferences"""
        await self.connect()
        
        async with self.pool.acquire() as connection:
            query = """
                INSERT INTO user_preferences (
                    keycloak_user_id, categories, keywords, 
                    email_notifications, created_at
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """
            
            row = await connection.fetchrow(
                query,
                user_id,
                json.dumps(preferences.get('categories', [])),
                json.dumps(preferences.get('keywords', [])),
                preferences.get('email_notifications', False),
                datetime.now()
            )
            
            return row['id'] if row else None
        
    async def cleanup_test_data(self):
        """Clean up all test data"""
        await self.connect()
        
        # Clean in correct order due to foreign keys
        tables = [
            'user_saved_papers',
            'user_preferences', 
            'papers',
            'pipeline_runs'
        ]
        
        async with self.pool.acquire() as connection:
            for table in tables:
                await connection.execute(
                    f"DELETE FROM {table} WHERE created_at > NOW() - INTERVAL '1 day'"
                )
            
    async def get_paper_count(self) -> int:
        """Get total paper count"""
        await self.connect()
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT COUNT(*) as count FROM papers")
            return row['count'] if row else 0
