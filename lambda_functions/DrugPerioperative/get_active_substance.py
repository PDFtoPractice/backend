import re
import boto3

def get_active_substance(drug):
     dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
     table = dynamodb.Table('product_active')
     
     first_word = re.sub(r'(\w*)\s.*', r'\1', drug)
     
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
             # if there is no active substance entry then assume first word is an active substance
             return first_word
     else:
         return first_word
         
     return active_substance