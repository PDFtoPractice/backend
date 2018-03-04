import boto3
from boto3.dynamodb.conditions import Key, Attr
import create_card
from get_drug_aliases import get_aliases
from get_active_substance import get_active_substance


def get_documents(drugA):
    '''Find mentions of drug B in a leaflet (or spc) of drug A'''

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('drugs')
    
    link = ""
    advice = ""
    items = []
    
    active_substance = get_active_substance(drugA)
    
    if active_substance:  # Drug was a valid product name
        # Case of drug A being a product name
        response = table.query(
             KeyConditionExpression=Key('active_substance').eq(active_substance) & Key('product').eq(drugA.upper())
        )
        if 'Items' in response and not response['Items']==[]:
            items = response['Items']
    else:  # Try interpreting drug A as an active substance
        active_substance = drugA.upper()
        print(active_substance)
        
        response = table.query(
            KeyConditionExpression=Key('active_substance').eq(active_substance.upper())
        )
        
        if 'Items' in response and not response['Items']==[] :
            items = response['Items']
        else:
            advice = "No documents found for " + drugA
    
    return items

 
