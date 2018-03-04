import boto3

def get_aliases(condition):
 dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
 table = dynamodb.Table('condition')
 
 aliases = [condition.lower(), condition.capitalize()]
 
 response = table.get_item(
        Key={
            'condition': condition.lower(),
        }
    )
    
 if 'Item' in response:
     item = response['Item']
     if 'aliases' in item:
         aliases = item['aliases']
     else:
         return aliases
 else:
     return aliases
 
 aliases.append(condition.lower())
 
 all_aliases = []
 for alias in aliases:
     all_aliases.append(alias)
     all_aliases.append(alias.capitalize())
 
 # print(all_aliases)
 
 return all_aliases