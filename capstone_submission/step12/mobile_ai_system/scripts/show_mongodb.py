from mobile_ai_system.infrastructure.persistence.mongodb.client import MongoDBClient

mongo = MongoDBClient()

collection = mongo.db["operator_events"]

print(f"Documents: {collection.count_documents({})}")

print()

for doc in collection.find().limit(5):
    print(doc)