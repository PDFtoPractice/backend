import pandas as pd
import boto3

# Read csv file into data frame
dataFrame = pd.read_csv('/Users/gordonbuck/Documents/PyCharmProjects/GroupProject/backend/src/csv_parser/csv/drug_instructions.csv')

# Get database resource
dynamodb = boto3.resource('dynamodb')

# Create table for CSV data
table = dynamodb.create_table(
    TableName='csv_advice',
    KeySchema=[
        {
            'AttributeName': 'drug',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'drug',
            'AttributeType': 'S'
        }

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait for the table to exist
table.meta.client.get_waiter('table_exists').wait(TableName='csv_advice')

# Batch write the csv pairs to the created table
with table.batch_writer() as batch:
    for it in dataFrame.itertuples():
        batch.put_item(
            Item={
                'drug': it[1],
                'advice': it[2],
            }
        )
