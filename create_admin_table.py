
import boto3
from getpass import getpass
from werkzeug.security import generate_password_hash
from botocore.exceptions import ClientError

REGION = "us-east-1"
ADMIN_NAME = "Krishna Nand Jha"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
admin_table = dynamodb.Table("admins")


def create_admin():
    email = input("Enter your admin email: ").strip().lower()
    password = getpass("Set your admin password (input hidden): ")

    if not email or not password:
        print("Email and password cannot be empty.")
        return

    if len(password) < 12:
        print("Use a password with at least 12 characters.")
        return

    try:
        admin_table.put_item(
            Item={
                "email": email,
                "name": ADMIN_NAME,
                "password": generate_password_hash(password),
                "role": "admin",
            },
            ConditionExpression="attribute_not_exists(email)",
        )
        print(f"Admin account created for {ADMIN_NAME} ({email}).")

    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print("An admin account with this email already exists.")
            print("No existing account was overwritten.")
        else:
            raise


if __name__ == "__main__":
    create_admin()
