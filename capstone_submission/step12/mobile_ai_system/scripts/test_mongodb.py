"""
Simple MongoDB connectivity test.
"""

from mobile_ai_system.infrastructure.persistence.mongodb.client import MongoDBClient


def main():

    mongo = MongoDBClient()

    print()
    print("=" * 50)
    print("MongoDB Connection Test")
    print("=" * 50)

    if not mongo.health_check():
        print("✗ Connection failed")
        return

    print("✓ Connected successfully")

    collection = mongo.db["operator_events"]

    count = collection.count_documents({})

    print(f"\nCollection contains {count} documents")

    if count == 0:
        print("No documents found.")
        mongo.close()
        return

    print("\nSample documents:")

    for doc in collection.find().limit(5):
        print(doc)

    print("\nSearching by operator name...")

    events = mongo.search_events(
        operator_name="Verizon Communications"
        )
    print(f"Retrieved {len(events)} documents")
    
    for event in events[:3]:
        print(event["operator_name"], "-", event["event_category"])
    

    mongo.close()


if __name__ == "__main__":
    main()