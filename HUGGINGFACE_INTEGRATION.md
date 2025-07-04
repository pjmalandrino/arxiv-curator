# ArXiv Curator - HuggingFace Integration Guide

## Current Setup

Your ArXiv curator now uses HuggingFace's serverless inference API instead of local Ollama.

### Configuration

```bash
# .env file
POSTGRES_PASSWORD=your_secure_password_here
HF_TOKEN=your_huggingface_token_here
HF_MODEL=facebook/bart-large-cnn
```

### Running the Application

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f pipeline

# Run tests
docker-compose run --rm pipeline python test_hf_docker.py

# Stop services
docker-compose down
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  ArXiv API      │────▶│  Pipeline        │────▶│  PostgreSQL     │
│                 │     │  - Fetch papers  │     │  - Store papers │
└─────────────────┘     │  - Summarize     │     │  - Store summaries
                        │    via HF API    │     └─────────────────┘
                        └──────────────────┘              │
                                 │                        │
                                 ▼                        ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │                  │     │                 │
                        │  HuggingFace     │     │  Web Interface  │
                        │  Inference API   │     │  (Flask)        │
                        │                  │     │                 │
                        └──────────────────┘     └─────────────────┘
```

## Model Strategy

The `hf_client.py` is designed with a strategy pattern to easily switch between different model types:

- **BARTSummarizer**: Current implementation for BART-based models
- **InstructionSummarizer**: Ready for instruction-following models (when available)

## Customization Options

### 1. Change the Model

Edit `.env` to use a different model:
```bash
HF_MODEL=google/pegasus-xsum  # Alternative summarization model
```

### 2. Adjust Summary Parameters

Edit `hf_client.py` to modify:
- Summary length (`max_length`, `min_length`)
- Relevance scoring keywords
- Key points extraction logic

### 3. Add Better Relevance Scoring

Current implementation uses keyword matching. You could improve it by:
- Using embeddings for semantic similarity
- Training a classifier on ArXiv categories
- Using a dedicated relevance model

### 4. Handle Multiple Models

You could modify the pipeline to use different models for different tasks:
- One model for summarization
- Another for relevance scoring
- Another for key points extraction

## Monitoring & Debugging

### Check Model Status
```python
# In test_hf.py
import requests

headers = {"Authorization": f"Bearer {HF_TOKEN}"}
response = requests.get(
    f"https://api-inference.huggingface.co/status/{model}",
    headers=headers
)
print(response.json())
```

### Common Issues

1. **503 Error (Model Loading)**:
   - Normal on first use
   - Pipeline includes retry logic
   - Wait 20-60 seconds for model to load

2. **Rate Limits**:
   - Free tier has limits
   - Add delays between requests
   - Consider PRO account for higher limits

3. **Summary Quality**:
   - BART-CNN is trained on news, not academic papers
   - Consider fine-tuning or using specialized models

## Future Enhancements

1. **Use Dedicated Inference Endpoints**:
   - Deploy your own model instance
   - Better performance and reliability
   - Custom models possible

2. **Multi-Model Pipeline**:
   - Use different models for different paper categories
   - Ensemble approaches for better quality

3. **Fine-Tune on ArXiv Data**:
   - Train a model specifically on academic abstracts
   - Better domain-specific performance

4. **Add Embedding Search**:
   - Use sentence transformers for semantic search
   - Find similar papers
   - Better relevance scoring

## Cost Considerations

- **Current**: Free tier with rate limits
- **PRO Account**: $9/month for higher limits
- **Dedicated Endpoints**: Pay per hour for dedicated instances
- **Alternative**: Use HF Inference Endpoints for production

## Testing New Models

To test if a model is available:
```python
python pipeline/src/find_summarization_models.py
```

This will show you which models are currently available on the serverless API.
