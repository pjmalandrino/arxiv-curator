"""
Test data fixtures for arXiv curator tests
"""
from datetime import datetime, date

# Sample paper data for different test scenarios
TEST_PAPERS = [
    {
        'arxiv_id': '2401.00001',
        'title': 'Revolutionary Advances in Large Language Models: GPT-5 and Beyond',
        'authors': ['Sam Altman', 'Ilya Sutskever', 'Greg Brockman'],
        'abstract': '''This groundbreaking paper introduces GPT-5, a revolutionary large language model 
                     that achieves human-level performance across diverse tasks. We present novel architectural 
                     improvements including adaptive attention mechanisms and dynamic parameter allocation. 
                     Our model demonstrates unprecedented capabilities in reasoning, creativity, and factual accuracy.
                     Extensive benchmarks show state-of-the-art results on all major NLP tasks.''',
        'published_date': date(2024, 1, 20),
        'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
        'pdf_url': 'https://arxiv.org/pdf/2401.00001.pdf'
    },
    {
        'arxiv_id': '2401.00002',
        'title': 'Efficient Fine-tuning of LLMs with LoRA-Pro: A Novel Approach',
        'authors': ['Edward Hu', 'Yelong Shen', 'Phil Wang'],
        'abstract': '''We introduce LoRA-Pro, an enhanced version of Low-Rank Adaptation that enables 
                     efficient fine-tuning of large language models with minimal computational overhead. 
                     Our method reduces memory requirements by 90% while maintaining performance parity 
                     with full fine-tuning. We demonstrate effectiveness across multiple model architectures 
                     including LLaMA, GPT, and BERT variants.''',
        'published_date': date(2024, 1, 18),
        'categories': ['cs.LG', 'cs.CL'],
        'pdf_url': 'https://arxiv.org/pdf/2401.00002.pdf'
    },
    {
        'arxiv_id': '2401.00003',
        'title': 'Multimodal Foundation Models: Vision-Language Pre-training at Scale',
        'authors': ['Jiasen Lu', 'Dhruv Batra', 'Devi Parikh'],
        'abstract': '''This paper presents a comprehensive study on scaling vision-language pre-training 
                     to create powerful multimodal foundation models. We introduce CLIP-X, trained on 
                     10 billion image-text pairs, achieving remarkable zero-shot performance. Our analysis 
                     reveals emergent capabilities in visual reasoning and cross-modal understanding.''',
        'published_date': date(2024, 1, 15),
        'categories': ['cs.CV', 'cs.CL', 'cs.AI'],
        'pdf_url': 'https://arxiv.org/pdf/2401.00003.pdf'
    }
]

# Edge case papers for testing
EDGE_CASE_PAPERS = [
    {
        'arxiv_id': '2401.99999',
        'title': 'A' * 500,  # Very long title
        'authors': ['Author' + str(i) for i in range(50)],  # Many authors
        'abstract': 'Short abstract.',  # Very short abstract
        'published_date': date(2024, 1, 1),
        'categories': ['cs.CL'],
        'pdf_url': 'https://arxiv.org/pdf/2401.99999.pdf'
    },
    {
        'arxiv_id': '2401.00000',
        'title': 'Paper with Special Characters: <>&"\'',
        'authors': ["O'Brien", "Müller", "José García"],  # Authors with special characters
        'abstract': 'Abstract with special characters: <>&"\' and émojis 🚀',
        'published_date': date(2024, 1, 2),
        'categories': ['cs.AI', 'cs.RO', 'cs.HC', 'cs.CY'],  # Multiple categories
        'pdf_url': 'https://arxiv.org/pdf/2401.00000.pdf'
    }
]

# Expected summaries for test papers
TEST_SUMMARIES = {
    '2401.00001': {
        'summary': 'GPT-5 achieves human-level performance with novel architectures including adaptive attention.',
        'key_points': [
            'Introduces GPT-5 with human-level performance',
            'Novel adaptive attention mechanisms',
            'Dynamic parameter allocation',
            'State-of-the-art results on all NLP benchmarks'
        ],
        'relevance_score': 10.0,
        'model_used': 'facebook/bart-large-cnn'
    },
    '2401.00002': {
        'summary': 'LoRA-Pro enables efficient LLM fine-tuning with 90% memory reduction.',
        'key_points': [
            'Enhanced Low-Rank Adaptation method',
            '90% memory reduction',
            'Maintains performance parity',
            'Works with LLaMA, GPT, and BERT'
        ],
        'relevance_score': 9.0,
        'model_used': 'facebook/bart-large-cnn'
    }
}

# Mock API responses
MOCK_ARXIV_RESPONSE = {
    'entries': [
        {
            'id': 'http://arxiv.org/abs/2401.00001v1',
            'updated': '2024-01-20T00:00:00Z',
            'published': '2024-01-20T00:00:00Z',
            'title': 'Revolutionary Advances in Large Language Models',
            'summary': 'This groundbreaking paper introduces GPT-5...',
            'authors': [{'name': 'Sam Altman'}, {'name': 'Ilya Sutskever'}],
            'categories': [{'term': 'cs.CL'}, {'term': 'cs.AI'}],
            'links': [{'href': 'http://arxiv.org/pdf/2401.00001v1', 'type': 'application/pdf'}]
        }
    ]
}

# Scoring test cases
SCORING_TEST_CASES = [
    {
        'paper': TEST_PAPERS[0],  # GPT-5 paper
        'expected_scores': {
            'keyword_score': 10.0,  # Contains LLM, language model
            'author_score': 8.0,    # Well-known authors
            'temporal_score': 9.0,  # Recent publication
            'composite_score': 9.0  # High overall relevance
        }
    },
    {
        'paper': TEST_PAPERS[2],  # Multimodal paper
        'expected_scores': {
            'keyword_score': 5.0,   # Less relevant to LLM
            'author_score': 6.0,    # Known authors
            'temporal_score': 8.0,  # Recent
            'composite_score': 6.3  # Medium relevance
        }
    }
]