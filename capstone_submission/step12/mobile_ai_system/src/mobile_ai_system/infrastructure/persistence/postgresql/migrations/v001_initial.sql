CREATE TABLE IF NOT EXISTS episodes (

    episode_id UUID PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,

    user_request TEXT NOT NULL,

    workflow_state JSONB NOT NULL,

    evaluation_score DOUBLE PRECISION

);