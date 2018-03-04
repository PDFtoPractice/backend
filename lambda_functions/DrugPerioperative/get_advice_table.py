import boto3
import json
import re
from boto3.dynamodb.conditions import Key, Attr
import create_card


def get_advice(drug, active):
    '''Extract advice from csv_advice table'''

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('perioperative_table')
    
    source = "A Guide to The Administration Of Medicines in the Peri-operative Period"
    link = "http://foi.nhsgrampian.org/globalassets/foidocument/dispublicdocuments---all-documents/PeriOp_697_0714.pdf"
    
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
        notes = item['notes']
        advice += "<br><br>Notes: " + notes if len(notes)>5 else ""
        risks = item['risks']
        advice += "<br><br>Risks: " + risks if len(risks)>5 else ""
        advice = re.sub(r'\n', r"<br>", advice)
        
    else:
        advice = "No advice found for " + drug
    
    card = create_card.card(None, source, link, drug, advice)
    
    return card

 
