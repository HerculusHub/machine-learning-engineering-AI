-- ============================================================
-- Mobile AI System
-- PostgreSQL Schema
-- Architecture v2.0 (Frozen)
-- ============================================================

CREATE TABLE IF NOT EXISTS episodes (

    episode_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    user_request TEXT NOT NULL,

    workflow_state JSONB NOT NULL,

    evaluation_score DOUBLE PRECISION,

    metadata JSONB DEFAULT '{}'

);

CREATE TABLE IF NOT EXISTS reflections (

    reflection_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    lesson TEXT NOT NULL,

    source TEXT,

    score DOUBLE PRECISION,

    metadata JSONB DEFAULT '{}'

);

CREATE TABLE IF NOT EXISTS semantic_memory (

    knowledge_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    category TEXT NOT NULL,

    item JSONB NOT NULL,

    metadata JSONB DEFAULT '{}'

);

CREATE TABLE IF NOT EXISTS execution_history (

    execution_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    workflow_id UUID,

    agent_name TEXT,

    action TEXT,

    duration_ms DOUBLE PRECISION,

    status TEXT,

    metadata JSONB DEFAULT '{}'

);

CREATE INDEX IF NOT EXISTS idx_episode_time
ON episodes(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reflection_time
ON reflections(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reflection_score
ON reflections(score DESC);

CREATE INDEX IF NOT EXISTS idx_semantic_category
ON semantic_memory(category);

CREATE INDEX IF NOT EXISTS idx_execution_agent
ON execution_history(agent_name);

CREATE INDEX IF NOT EXISTS idx_execution_time
ON execution_history(created_at DESC);