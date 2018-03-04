import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import get_advice_csv, get_advice_table
from get_active_substance import get_active_substance


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
    '''Simple HTTP endpoint using API Gateway. Handles requests of the form
    https://yzs63ht9tg.execute-api.eu-west-1.amazonaws.com/prod/DrugPerioperative?drug=Aspirin
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('csv_advice')

    payload = event['queryStringParameters']
    if not 'drug' in payload:
        return respond(None, {"message": "Error in specifing request parameters"})
    drug = payload['drug'] 
    
    active = get_active_substance(drug.upper())
    if active:
        print(active)
        active = active.capitalize()
    
    card1 = get_advice_csv.get_advice(drug, active)
    card2 = get_advice_table.get_advice(drug, active)
    
    return respond(None, [card1, card2])

 
