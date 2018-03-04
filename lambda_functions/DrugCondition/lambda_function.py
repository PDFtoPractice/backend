import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import find_mentions_in_leaflet 
from get_aliases import get_aliases


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
    if not 'drug' in payload or not 'condition' in payload:
        return respond(None, {"message": "Error in specifing request parameters"})
    drug = payload['drug']
    condition = payload['condition']
    
    aliases=get_aliases(condition)
    
    card1 = find_mentions_in_leaflet.get_advice(drug, condition, spc=False, aliases_of_condition=aliases)
    card2 = find_mentions_in_leaflet.get_advice(drug, condition, spc=True, aliases_of_condition=aliases)

    return respond(None, [card1, card2])

 

