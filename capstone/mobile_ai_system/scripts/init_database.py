from mobile_ai_system.infrastructure.persistence.postgresql.schema import (
    SchemaManager,
)

if __name__ == "__main__":

    SchemaManager().initialize()

    print("Database initialized successfully.")