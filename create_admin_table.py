import boto3
from werkzeug.security import generate_password_hash

# Connect to DynamoDB (make sure AWS credentials are configured)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # change region if needed

# Check if table exists
existing_tables = dynamodb.meta.client.list_tables()['TableNames']

if 'admins' in existing_tables:
    admin_table = dynamodb.Table('admins')
    print("Table 'admins' already exists.")
else:
    # Create the admins table in on-demand mode (no ProvisionedThroughput needed)
    admin_table = dynamodb.create_table(
        TableName='admins',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
   # ✅ auto scales, simpler for demo apps
    )
    admin_table.meta.client.get_waiter('table_exists').wait(TableName='admins')
    admin_table.load()
    print("✅ Table 'admins' created successfully!")

# Function to insert admin account
def create_admin(email, name, password):
    hashed_password = generate_password_hash(password)
    admin_table.put_item(
        Item={
            'email': email,
            'name': name,
            'password': hashed_password,
            'role': 'admin'
        }
    )
    print(f"✅ Admin account created for {name} ({email})")

if __name__ == "__main__":
    # Replace with your own details
    create_admin("mayankchauhan.61z1@gmail.com", "Mayank Chauhan", "BUKMI@12345")
    create_admin("mayank.chauhan5002@gmail.com", "Mayank Chauhan", "BUKMI")
