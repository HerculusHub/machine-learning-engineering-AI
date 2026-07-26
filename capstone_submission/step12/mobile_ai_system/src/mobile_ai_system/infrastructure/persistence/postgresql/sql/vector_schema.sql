CREATE TABLE IF NOT EXISTS vector_embeddings (

    embedding_id UUID PRIMARY KEY,

    entity_type VARCHAR(50) NOT NULL,

    entity_id UUID NOT NULL,

    embedding_model VARCHAR(100) NOT NULL,

    embedding_dimension INTEGER NOT NULL,

    embedding JSONB,

    metadata JSONB,

    created_at TIMESTAMP NOT NULL

);

CREATE INDEX IF NOT EXISTS idx_vector_entity
ON vector_embeddings(
    entity_type,
    entity_id
);