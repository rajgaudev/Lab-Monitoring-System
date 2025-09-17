import json
import boto3
from decimal import Decimal

# Initialize DynamoDB 
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LabMonitoring')

# Recursively convert float values to Decimal (DynamoDB requirement)
def convert_floats(obj):
    if isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))  # Convert float to Decimal
    else:
        return obj

# Main Lambda handler
def lambda_handler(event, context):
    try:
        # Parse incoming JSON body
        body = json.loads(event['body'])
        
        # Convert floats to Decimals for DynamoDB
        body = convert_floats(body)

        # Put the item into DynamoDB (overwrites if same device_name exists)
        table.put_item(Item=body)

        return {
            'statusCode': 200,
            'body': json.dumps("Data stored successfully!")
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }


