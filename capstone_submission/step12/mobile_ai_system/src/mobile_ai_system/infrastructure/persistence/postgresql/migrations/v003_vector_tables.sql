CREATE TABLE IF NOT EXISTS vector_embeddings (

    embedding_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    object_type TEXT NOT NULL,

    object_id UUID NOT NULL,

    embedding BYTEA,

    metadata JSONB

);