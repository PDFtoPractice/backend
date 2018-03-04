import create_card
import re
from get_drug_aliases import get_aliases
from get_active_substance import get_active_substance


def get_advice(drugA, drugB, items, spc=False, aliases_of_B=None):
    '''Find mentions of drug B in a leaflet (or spc) of drug A'''
   
    document = 'spc' if spc else 'leaflet'

    link = ""
    advice = ""
    product = None
    #alery_words = ["alergy", "Alergy", "allergic", "Hypersensitivity", "hypersensitivity"]
    
    if not items:
        #advice = "No " + document + " found for " + drugA
        return None
  
    for item in items:
        if document in item:    #take the first leaflet that matches
            leaflet = item[document] 
            product = item['product']
            link = leaflet['link']
            paragraphs = leaflet['paragraphs']
            for paragraph in paragraphs:
                found = False
                for alias in aliases_of_B:
                    if alias in paragraph:
                        #paragraph_about_alergy = False
                        #for word in alery_words:
                        #    if word in paragraph:
                        #        paragraph_about_alergy = True
                        #if not paragraph_about_alergy:
                        found = True
                        paragraph = re.sub(alias, '<b><span class="highlight">'+alias+'</span></b>', paragraph)
                if found:
                    # paragraph = re.sub('<span class="highlight">(.*)</span>', '<span class="highlight"><a matTooltip="Alias for '+drugB+r'">\1</span>', paragraph)
                    paragraph = re.sub('\(cid:129\)','-',paragraph)
                    advice += paragraph + "<br><br>"
            break
                   
    if not advice:
        advice = "No interaction for the following medications  (" + drugA.lower() + ", " + drugB.lower() + ") were found in this document but we still recommend contacting your doctor "
        
    if spc:
        source = "Summary Of Product Characteristics of "
    else:
        source = "Leaflet of "
    source += product + " (" + drugA + ") " if product and not product==drugA else drugA
    
    card = create_card.card(None, source, link, advice)
    
    return card

 
