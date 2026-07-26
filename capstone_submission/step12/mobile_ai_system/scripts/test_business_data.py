from mobile_ai_system.infrastructure.persistence.csv import (
    CustomerDataClient,
)


def main():

    client = CustomerDataClient()

    df = client.load()

    print()

    print("=" * 50)
    print("Business Database Test")
    print("=" * 50)

    print()

    print(f"Rows: {client.row_count()}")

    print()

    print(f"Columns:")

    for c in client.columns():
        print(c)

    print()

    print(df.head())


if __name__ == "__main__":
    main()