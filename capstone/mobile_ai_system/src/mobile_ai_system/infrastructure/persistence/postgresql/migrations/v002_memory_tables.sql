-- ==========================================================
-- Reflection Memory
-- ==========================================================

CREATE TABLE IF NOT EXISTS reflections (

    reflection_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    lesson TEXT NOT NULL,

    source TEXT,

    score DOUBLE PRECISION,

    metadata JSONB

);

-- ==========================================================
-- Semantic Memory
-- ==========================================================

CREATE TABLE IF NOT EXISTS semantic_memory (

    knowledge_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    category TEXT NOT NULL,

    content JSONB NOT NULL,

    confidence DOUBLE PRECISION,

    source TEXT

);

-- ==========================================================
-- Execution History
-- ==========================================================

CREATE TABLE IF NOT EXISTS execution_history (

    execution_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    episode_id UUID,

    agent_name TEXT NOT NULL,

    iteration INTEGER,

    input_state JSONB,

    output_state JSONB,

    duration_ms DOUBLE PRECISION,

    status TEXT,

    FOREIGN KEY (episode_id)
        REFERENCES episodes(episode_id)
        ON DELETE CASCADE

);