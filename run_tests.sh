#!/bin/bash
# Simple test runner script

echo "Running ArXiv Curator Tests..."
echo "============================="

# Test imports
echo "Testing Python imports..."
docker run --rm -v $(pwd):/app -w /app arxiv-curator-pipeline python -c "
import sys
sys.path.insert(0, '/app')
try:
    from src.core.config import Config
    from src.domain.entities import Paper
    from src.infrastructure.arxiv import ArxivClient
    from src.services.curation_service import CurationService
    print('✓ All imports successful!')
except Exception as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"

# Test configuration
echo ""
echo "Testing configuration..."
docker run --rm -v $(pwd):/app -w /app -e HF_TOKEN=test_token arxiv-curator-pipeline python -c "
import sys
sys.path.insert(0, '/app')
try:
    from src.core.config import Config
    config = Config.from_environment()
    print('✓ Configuration loaded successfully!')
except Exception as e:
    print(f'✗ Configuration error: {e}')
"

echo ""
echo "Testing domain models..."
docker run --rm -v $(pwd):/app -w /app arxiv-curator-pipeline python -c "
import sys
from datetime import date
sys.path.insert(0, '/app')
try:
    from src.domain.entities import PaperMetadata, Paper
    from src.domain.value_objects import ArxivId, Score, Category
    
    # Test ArxivId
    arxiv_id = ArxivId('2301.12345')
    assert str(arxiv_id) == '2301.12345'
    
    # Test Score
    score = Score(0.75)
    assert float(score) == 0.75
    assert score.is_above_threshold(0.5)
    
    # Test Category
    category = Category('cs.AI')
    assert category.get_primary() == 'cs'
    assert category.get_subcategory() == 'AI'
    
    # Test PaperMetadata
    metadata = PaperMetadata(
        arxiv_id='2301.12345',
        title='Test Paper',
        authors=['Author One'],
        abstract='Test abstract',
        published_date=date.today(),
        categories=['cs.AI'],
        pdf_url='https://test.pdf'
    )
    
    # Test Paper
    paper = Paper.from_arxiv_data({
        'arxiv_id': '2301.12345',
        'title': 'Test Paper',
        'authors': ['Author One'],
        'abstract': 'Test abstract',
        'published_date': date.today(),
        'categories': ['cs.AI'],
        'pdf_url': 'https://test.pdf'
    })
    
    print('✓ Domain models working correctly!')
except Exception as e:
    print(f'✗ Domain model error: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "All tests completed!"
