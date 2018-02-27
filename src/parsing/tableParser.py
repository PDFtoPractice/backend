import pandas
import boto3

dynamodb = boto3.resource('dynamodb')

df = pandas.read_csv('/Users/gordonbuck/Documents/PyCharmProjects/GroupProject/backend/src/parsing/tables/merged_tables.csv')
'''
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
'''
table.meta.client.get_waiter('table_exists').wait(TableName='perioperative_table')

table = dynamodb.Table('perioperative_table')

with table.batch_writer() as batch:
    for index, row in df.iterrows():
        drugs = row['Drug Examples']
        if drugs != drugs:
            continue
        drugs = drugs.split(' ')
        for drug in drugs:
            if drug == '\n':
                continue
            drug = drug.replace(',','')
            risks = row['\nRisks/ Cautions/Contraindications \n']
            advice = row['Recommendations']
            notes = row[' \nNotes \n ']
            batch.put_item(
                Item={
                    'drug': drug,
                    'risks': risks if risks == risks else ' ',
                    'advice': advice if advice == advice else ' ',
                    'notes': notes if notes == notes else ' '
                }
            )
