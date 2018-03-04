import re
import boto3

def get_active_substance(drug):
 dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
 table = dynamodb.Table('product_active')
 
 response = table.get_item(
        Key={
            'product': drug.lower(),
        }
    )
    
 if 'Item' in response:
     item = response['Item']
     if 'active' in item:
         active_substance = item['active'][0]
     else:
         return None
 else:
     return None
     
 return active_substance.upper()