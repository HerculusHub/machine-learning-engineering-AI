CREATE TABLE IF NOT EXISTS vector_embeddings (
    embedding_id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- future pgvector column (disabled for now)
    embedding VECTOR(1536),

    source_type TEXT,
    source_id TEXT,

    metadata JSONB
);