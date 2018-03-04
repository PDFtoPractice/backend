import boto3
from boto3.dynamodb.conditions import Key, Attr
import create_card
from get_active_substance import get_active_substance


def get_advice(drugA,drugB,activeA,activeB):
    '''Extract advice from csv_advice table'''

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('interactions')
    
    source = "National Institute for Health and Care Excellence"
    link = "https://bnf.nice.org.uk/interaction/"
    advice = ""
    
    if activeA:
        drugA = activeA
    if activeB:
        drugB = activeB
    
    response = table.get_item(
        Key={
            'drug': drugA.capitalize(),
        }
    )
    
    drugB = drugB.capitalize()
    
    if 'Item' in response:
        item = response['Item']
        data = item['data'] 
        for entry in data:
           interactant = entry['interactant']
           if interactant == drugB or drugB.startswith(interactant) or interactant.startswith(drugB):
               evidence_for_interaction = entry['evidence_for_interaction'] 
               severity_of_interaction = entry['severity_of_interaction']
               message = entry['message']
               advice = message
               advice += "<br>Evidence for interaction: " + evidence_for_interaction if evidence_for_interaction else ""
               advice += "<br>Severity of interaction: " + severity_of_interaction if severity_of_interaction else ""
               if advice.endswith(" in"):
                   advice += ' <a href="https://bnf.nice.org.uk/guidance/guidance-on-prescribing.html">Guidance on Prescribing</a>)'
               break
    else:
        advice = "No advice found for " + drugA
        
    if not advice:
        advice = "No interactions for the following medications (" + drugA.lower() + ", " + drugB.lower() + ") were found but we still recommend contacting your doctor."
    
   
    
    card = create_card.card(None, source, link, advice)
    
    return card

 
