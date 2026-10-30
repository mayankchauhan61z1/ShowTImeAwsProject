import boto3

REGION = "us-east-1"
dynamodb = boto3.client("dynamodb", region_name=REGION)

tables = {
    "users": [("email", "HASH")],
    "admins": [("email", "HASH")],
    "ContactForm": [("email", "HASH")],
    "bookings": [("user_email", "HASH"), ("booking_id", "RANGE")],
    "moviesdata": [("movie_id", "HASH")],
}

for name, keys in tables.items():
    existing = dynamodb.list_tables()["TableNames"]

    if name in existing:
        print(f"Already exists: {name}")
        continue

    schema = [
        {"AttributeName": key, "KeyType": kind}
        for key, kind in keys
    ]
    attributes = [
        {"AttributeName": key, "AttributeType": "S"}
        for key, _ in keys
    ]

    print(f"Creating: {name}")
    dynamodb.create_table(
        TableName=name,
        KeySchema=schema,
        AttributeDefinitions=attributes,
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb.get_waiter("table_exists").wait(TableName=name)
    print(f"Ready: {name}")

print("All table setup checks completed.")
