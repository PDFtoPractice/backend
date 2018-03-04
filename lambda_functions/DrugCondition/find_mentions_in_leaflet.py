import boto3
import re
from boto3.dynamodb.conditions import Key, Attr
import create_card
from get_aliases import get_aliases
from get_active_substance import get_active_substance


def get_advice(drug, condition, spc=False, aliases_of_condition=None):
    '''Find mentions of condition in a leaflet (or spc) of a drug'''

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('drugs')
    
    document = 'spc' if spc else 'leaflet'

    link = ""
    advice = ""
    items = []
    product = None
    
    active_substance = get_active_substance(drug)
    
    if active_substance:  # Drug was a valid product name
        response = table.query(
            KeyConditionExpression=Key('active_substance').eq(active_substance) & Key('product').eq(drug.upper())
        )
        if 'Items' in response and not response['Items']==[]:
            items = response['Items']
    else:  # Try interpreting drug A as an active substance
        active_substance = drug.upper()

        response = table.query(
            KeyConditionExpression=Key('active_substance').eq(active_substance)
        )
        
        if 'Items' in response and not response['Items']==[] :
            items = response['Items']
        else:
            advice = "No " + document + " found for " + drug
    
    if not aliases_of_condition:
        aliases_of_condition = get_aliases(condition)
    
    for item in items:
        if document in item:    #take the first leaflet that matches
            leaflet = item[document] 
            product = item['product']
            link = leaflet['link']
            paragraphs = leaflet['paragraphs']
            print(len(paragraphs), "---------------")
            for paragraph in paragraphs:
                found = False
                for alias in aliases_of_condition:
                    if alias in paragraph:
                        found = True
                        paragraph = re.sub(alias, '<span class="highlight"><b>'+alias+'</b></span>', paragraph)
                if found:
                    paragraph = re.sub('<span class="highlight">(.*)</span>', '<span class="highlight"><a mattooltip="Alias for '+condition+r'">\1</span>', paragraph)
                    paragraph = re.sub('\(cid:129\)','-',paragraph)
                    advice += paragraph + "<br><br>"
            break
                   
    if not advice:
        advice = "No interactions for the following medication and condition were found but we still recommend contacting your doctor "
    
    
    if spc:
        source = "Summary Of Product Characteristics of "
    else:
        source = "Leaflet of " 
    source += product if product else drug
        
    card = create_card.card(None, source, link, advice)
    
    return card

 
