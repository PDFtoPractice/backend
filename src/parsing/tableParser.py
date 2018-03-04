import pandas
import boto3

# Get database resource
dynamodb = boto3.resource('dynamodb')

# Read in the table (which has been exported manually to a csv)
df = pandas.read_csv('/Users/gordonbuck/Documents/PyCharmProjects/GroupProject/backend/src/parsing/tables/merged_tables.csv')

# Create table in the database
table = dynamodb.create_table(
    TableName='perioperative_table',
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

# Wait for table to exist
table.meta.client.get_waiter('table_exists').wait(TableName='perioperative_table')

# Initiate batch write
with table.batch_writer() as batch:
    for index, row in df.iterrows():
        # Fetch attributes in the row
        drugs = row['Drug Examples']
        risks = row['\nRisks/ Cautions/Contraindications \n']
        advice = row['Recommendations']
        notes = row[' \nNotes \n ']

        # Drugs is empty (nan in csv)
        if drugs != drugs:
            continue

        # Generate list of drugs
        drugs = drugs.split(' ')

        # For each drug upload
        for drug in drugs:

            # Skip over non-drugs
            if drug == '\n':
                continue

            # Remove commas if the drugs were comma-seperated
            drug = drug.replace(',','')

            # Put item in database, replacing nans with spaces to indicate no attribute
            batch.put_item(
                Item={
                    'drug': drug,
                    'risks': risks if risks == risks else ' ',
                    'advice': advice if advice == advice else ' ',
                    'notes': notes if notes == notes else ' '
                }
            )
