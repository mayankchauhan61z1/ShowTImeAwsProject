import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# Check if table already exists


#======================
# Users table 
#======================

existing_tables = [t.name for t in dynamodb.tables.all()]
if 'users' in existing_tables:
    users_table = dynamodb.Table('users')
    print("Table 'users' already exists.")
else:
    # Create DynamoDB table
    users_table = dynamodb.create_table(
        TableName='users',
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
    )
    # Wait until table exists
    users_table.meta.client.get_waiter('table_exists').wait(TableName='users')
    users_table.load()
    print("Table 'users' created successfully!")

#======================
# Admins table 
#====================== 

# if 'admins' in existing_tables:
#     admin_table = dynamodb.Table('admins')
#     print("Table 'admins' already exists.")
# else:
#     admin_table = dynamodb.create_table(
#         TableName='admins',
#         KeySchema=[
#             {'AttributeName': 'email', 'KeyType': 'HASH'}
#         ],
#         AttributeDefinitions=[
#             {'AttributeName': 'email', 'AttributeType': 'S'}
#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 5,
#             'WriteCapacityUnits': 5
#         }
#     )
#     admin_table.meta.client.get_waiter('table_exists').wait(TableName='admins')
#     admin_table.load()
#     print("Table 'admins' created successfully!")

# ======================
# Contact Form table
# ======================

if 'ContactForm' in existing_tables:
    contact_table = dynamodb.Table('ContactForm')
    print("Table 'ContactForm' already exists.")
else:
    contact_table = dynamodb.create_table(
        TableName='ContactForm',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'}  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    contact_table.meta.client.get_waiter('table_exists').wait(TableName='ContactForm')
    contact_table.load()
    print("Table 'ContactForm' created successfully!")

#=======================
# Bookings table
#=======================

if 'bookings' in existing_tables:
    bookings_table = dynamodb.Table('bookings')
    print("Table 'bookings' already exists.")
else:
    bookings_table = dynamodb.create_table(
        TableName='bookings',
        KeySchema=[
            {'AttributeName': 'user_email', 'KeyType': 'HASH'},   # Partition Key
            {'AttributeName': 'booking_id', 'KeyType': 'RANGE'}   # Sort Key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'user_email', 'AttributeType': 'S'},
            {'AttributeName': 'booking_id', 'AttributeType': 'N'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    bookings_table.meta.client.get_waiter('table_exists').wait(TableName='bookings')
    bookings_table.load()

# print("Table 'bookings' created successfully!")
# print out some data about the table   
# print("Table name: ",table.table_name)
# print("Item count: ",table.item_count)
