from __future__ import print_function # Python 2/3 compatibility
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

table = dynamodb.Table('leaflet_links')

print('Loaded table')
data = json.load(open('all_links.json'))
for drug in data:

    print("Inserting: {Drug: " + drug+"}")
    table.put_item(
        Item={
            'drug': drug,
            'data': data[drug],
         }
     )
