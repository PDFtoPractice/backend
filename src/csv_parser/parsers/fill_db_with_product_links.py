from __future__ import print_function # Python 2/3 compatibility
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

table = dynamodb.Table('product_links')

print('Loaded table')
data = json.load(open('1000.json'))
for drug in data:
    for element in data[drug]:
        link = element['link']
        pdf_name = element['pdf_name']
        product = element['product']

        print("Inserting: {Drug: " + drug,
              "link: " + link + "}")
        table.put_item(
            Item={
                'drug': drug,
                'link': link,
                'pdf_name': pdf_name,
                'product': product,
             }
         )
