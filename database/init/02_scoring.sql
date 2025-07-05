-- Add scoring columns to summaries table
ALTER TABLE summaries 
ADD COLUMN IF NOT EXISTS score_explanation TEXT,
ADD COLUMN IF NOT EXISTS score_components JSONB;

-- Create a dedicated scores table for detailed tracking
CREATE TABLE IF NOT EXISTS paper_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    total_score FLOAT NOT NULL,
    llm_score FLOAT,
    keyword_score FLOAT,
    citation_score FLOAT,
    temporal_score FLOAT,
    author_score FLOAT,
    explanation TEXT,
    components JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_paper_scores_paper_id ON paper_scores(paper_id);
CREATE INDEX idx_paper_scores_total_score ON paper_scores(total_score DESC);
CREATE INDEX idx_paper_scores_created_at ON paper_scores(created_at DESC);

-- Create a view for easy querying of top papers
CREATE OR REPLACE VIEW top_scored_papers AS
SELECT 
    p.*,
    ps.total_score,
    ps.explanation as score_explanation,
    s.summary,
    s.key_points
FROM papers p
JOIN paper_scores ps ON p.id = ps.paper_id
LEFT JOIN summaries s ON p.id = s.paper_id
WHERE ps.total_score > 0.6
ORDER BY ps.total_score DESC, p.published_date DESC;
