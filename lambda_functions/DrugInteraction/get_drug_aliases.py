import boto3
import re

def get_aliases(drug, active):
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('aliases')
    
    drug = drug.lower()
    aliases = [drug]
    if active:
      active = active.lower()
   
    response = table.get_item(
           Key={
               'drug_name': drug,
           }
       )
       
    if 'Item' in response:
        item = response['Item']
        if 'aliases' in item:
            aliases = item['aliases']
            aliases.append(drug)
        else:
            return [drug, drug.upper(), drug.capitalize()]
    elif active:
        #drug = re.sub(r'(.*)\s\d.*', r'\1', drug)
        response = table.get_item(
           Key={
               'drug_name': active.lower(),
           }
        )
       
        if 'Item' in response:
            item = response['Item']
            if 'aliases' in item:
                aliases = item['aliases']
                aliases.append(drug)
        else:
            aliases.append(active)
            first_word = re.sub(r'(\w*)\s.*', r'\1', active)
            if not first_word == active:
                aliases.append(first_word)
    else:
        first_word = re.sub(r'(\w*)\s.*', r'\1', drug)
        if not first_word == drug:
            aliases.append(first_word)
    
    
    all_aliases = []
    for alias in aliases:
        all_aliases.append(alias)
        all_aliases.append(alias.capitalize())
    
    print(all_aliases)
 
    return all_aliases