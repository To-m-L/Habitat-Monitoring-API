import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HabitatData')

def validate_date(date_str):
    """
    Validate the format of the input date string.
    
    Parameters:
    date_str (str): The date string to validate.
    
    Returns:
    bool: True if the date string is valid, False otherwise.
    """
    try:
        # Try to create a datetime object with the given date string
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        # If a ValueError occurs, the date string is invalid
        return False

def lambda_handler(event, context):
    # Log the received event
    print(f"Received event: {json.dumps(event, indent=2)}")

    # Extract HTTP method and path parameters
    http_method = event.get('httpMethod', '')
    path_parameters = event.get('pathParameters', {})

    # Handle GET request without ID
    if http_method == 'GET' and not path_parameters:
        try:
            response = table.scan()
            data = response.get('Items', [])
            return {
                'statusCode': 200,
                'body': json.dumps(data)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error fetching data', 'error': str(e)})
            }

    # Handle GET request with ID
    elif http_method == 'GET' and 'id' in path_parameters:
        habitat_id = path_parameters['id']
        try:
            response = table.query(KeyConditionExpression=Key('HabitatID').eq(habitat_id))
            habitat = response["Items"]
            if habitat:
                return {
                    'statusCode': 200,
                    'body': json.dumps(habitat)
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': f'HabitatID {habitat_id} not found'})
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error fetching data', 'error': str(e)})
            }
            
    # Handle GET request with Date
    elif http_method == 'GET' and 'date' in path_parameters:
        habitat_date = path_parameters['date']
        try:
            response = table.query(IndexName = "DateIndex", KeyConditionExpression=Key('Date').eq(habitat_date))
            dateItems = response["Items"]
            if dateItems:
                return {
                    'statusCode': 200,
                    'body': json.dumps(dateItems)
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': f'No items on {habitat_date}'})
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error fetching data', 'error': str(e)})
            }
        
    # Handle POST request
    elif http_method == 'POST':
        try:
            # Parse the request body
            body = json.loads(event.get('body', '{}'))
            
            if(not body.get("HabitatID") or not body.get("Date") or not body.get("DataType") or not body.get('DataValue') or not body.get("SensorID")):
                raise ValueError("Missing required parameter(s)")
            
            
            
            # Extract data from the request body
            habitat_id = body.get('HabitatID')
            if(validate_date(body.get("Date"))):
                date = body.get('Date')
            else:
                raise ValueError("Date is not valid")
            data_type = body.get('DataType')
            data_value = body.get('DataValue')
            sensor_value = body.get("SensorID")
            
            # Insert data into DynamoDB table
            response = table.put_item(
                Item={
                    'HabitatID': habitat_id,
                    'Date': date,
                    'DataType': data_type,
                    'DataValue': data_value,
                    'SensorID': sensor_value
                }
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Data inserted successfully'})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error inserting data', 'error': str(e)})
            }
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': f'Method {http_method} not allowed'})
        }

