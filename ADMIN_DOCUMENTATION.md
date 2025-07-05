# Admin Dashboard Documentation

## Overview

The ArXiv Curator Admin Dashboard provides a web interface to manage the paper curation pipeline. It allows you to:

- Configure pipeline parameters
- Trigger manual pipeline runs
- Monitor pipeline status in real-time
- View database statistics
- Clear the database

## Accessing the Admin Dashboard

Navigate to `/admin` from your main application URL (e.g., `http://localhost:5000/admin`).

## Features

### 1. Statistics Overview
- Total papers in database
- Total summaries generated
- Latest and oldest paper dates

### 2. Pipeline Status
Real-time status monitoring showing:
- Current pipeline state (idle, running, completed, error)
- Progress percentage
- Detailed status messages

### 3. Pipeline Configuration

#### Days Back
- **Default**: 7 days
- **Range**: 1-30 days
- Controls how far back in time to fetch papers

#### Max Results
- **Default**: 10 papers
- **Range**: 1-100 papers
- Maximum number of papers to fetch per run

#### Batch Size
- **Default**: 5 papers
- **Range**: 1-20 papers
- Number of papers to process in each batch (affects API rate limiting)

#### Minimum Relevance Score
- **Default**: 0.4
- **Range**: 0.0-1.0
- Papers with scores below this threshold will be skipped

#### ArXiv Categories
Select from all available CS categories:
- cs.AI - Artificial Intelligence
- cs.CL - Computation and Language
- cs.CV - Computer Vision and Pattern Recognition
- cs.LG - Machine Learning
- And many more...

#### Keywords
Comma-separated list of keywords to filter papers. Examples:
- LLM, language model, transformer
- GPT, BERT, attention mechanism
- neural network, deep learning

### 4. Pipeline Triggering

Click the "Trigger Pipeline" button to start a new pipeline run. The pipeline will:
1. Fetch recent papers based on your configuration
2. Filter by categories and keywords
3. Generate summaries using HuggingFace models
4. Store results in the database

### 5. Database Management

The "Danger Zone" section allows you to clear all papers and summaries from the database. This action requires double confirmation and cannot be undone.

## Architecture

The admin module is cleanly separated from the main application:

```
src/
├── admin/
│   ├── __init__.py
│   └── routes.py     # Admin blueprint and routes
├── web_app.py        # Main web application
└── ...
```

The admin functionality is implemented as a Flask Blueprint, maintaining clean separation of concerns.

## Configuration Persistence

Admin configurations are stored in the `admin_config` table in PostgreSQL, ensuring settings persist across application restarts.

## Security Considerations

In production, consider:
- Adding authentication to the admin routes
- Implementing role-based access control
- Using HTTPS for secure communication
- Adding rate limiting for pipeline triggers
- Implementing audit logging

## Environment Variables

Ensure these are set in your `.env` file:
- `HF_TOKEN`: Your HuggingFace API token
- `HF_MODEL`: Model to use for summarization (default: facebook/bart-large-cnn)
- `POSTGRES_PASSWORD`: Database password