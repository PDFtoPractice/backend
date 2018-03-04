import boto3
from boto3.dynamodb.conditions import Key, Attr
import create_card


def get_advice(drug, active):
    '''Extract advice from csv_advice table'''

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('csv_advice')
    
    source = "Perioperative advice from RCoA's hackday"
    link = "https://github.com/dannyjnwong/PreopDrugs/blob/master/drug_instructions.csv"
    
    response = table.get_item(
        Key={
            'drug': drug,
        }
    )
    
    if not 'Item' in response and active:
        response = table.get_item(
            Key={
                'drug': active,
            }
        )
    
    if 'Item' in response:
        item = response['Item']
        advice = item['advice']
    else:
        advice = "No advice found for " + drug
    
    card = create_card.card(None, source, link, drug, advice)
    
    return card

 
