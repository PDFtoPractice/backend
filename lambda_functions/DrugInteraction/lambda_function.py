import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import find_mentions_in_nice, find_mentions_in_leaflet
from get_drug_aliases import get_aliases
from get_active_substance import get_active_substance
from get_documents import get_documents


print('Loading function')
dynamo = boto3.client('dynamodb')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin' : "*", # Required for CORS support to work
            "Access-Control-Allow-Credentials" : True # Required for cookies, authorization headers with HTTPS 
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('csv_advice')

    payload = event['queryStringParameters']
    if not 'drug1' in payload or not 'drug2' in payload:
        return respond(None, {"message": "Error in specifing request parameters"})
    drug1 = payload['drug1']
    drug2 = payload['drug2']
    
    active1 = get_active_substance(drug1)
    active2 = get_active_substance(drug2)
    
    aliases_of_1 = get_aliases(drug1, active1)
    aliases_of_2 = get_aliases(drug2, active2)
    
    documents1 = get_documents(drug1)
    documents2 = get_documents(drug2)
    
    cards = []
    
    
    card0 = find_mentions_in_nice.get_advice(drug1, drug2, active1, active2)
    if card0:
        cards.append(card0)
    print("Checkpoint 0---------")
    
    card1 = find_mentions_in_leaflet.get_advice(drug1, drug2, documents1, spc=False, aliases_of_B=aliases_of_2)
    if card1:
        cards.append(card1)
    print("Checkpoint 1 ---------")
    
    card2 = find_mentions_in_leaflet.get_advice(drug2, drug1, documents2, spc=False, aliases_of_B=aliases_of_1)
    if card2:
        cards.append(card2)
    print("Checkpoint 2---------")
    
    card3 = find_mentions_in_leaflet.get_advice(drug1, drug2, documents1, spc=True, aliases_of_B=aliases_of_2)
    if card3:
        cards.append(card3)
    print("Checkpoint 3---------")
    
    card4 = find_mentions_in_leaflet.get_advice(drug2, drug1, documents2, spc=True, aliases_of_B=aliases_of_1)
    if card4:
        cards.append(card4)
    print("Checkpoint 4---------")
   

    return respond(None, cards)

 
