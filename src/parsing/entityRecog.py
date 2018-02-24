# import GParser as GParser
# import ClearXML as ClearXML
# import extractParagraphs as ExtractParas
from parsing import GParser
import re
import spacy
urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492496435313.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510292397494.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1517548373003.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515735504413.pdf']
docs = [GParser.convert_pdf(url, format='text') for url in urls]
# xmldocs = [GParser.convert_pdf(url, format='xml') for url in urls]
# paras = [ExtractParas.extract_paragraphs(parsed) for parsed in xmldocs]

# extract headings paras
headings = ['1. What (\s)+ is and what is is used for', '2. What you need to know before you are given ProHance', '3. How you are given (\s)+', '4. Possible side effects', '5. How to store [\s]+', '6. Further Information']

def get_active_subst(text): # pass in text from drug's leaflet
    only_one = True    # whether there are more than one active substance to extract
    phrases = ['active substance is[\w\s]+.', 'active substances are([\w\s][,]*)+.', 'contains[\w\s]+ as the active ingredient', 'contains[\w]+ as the active ingredients', 'active ingredient is[\w\s]+.']
    match = [('active substance is', '', only_one), ('active substances are', '', not only_one), ('contains', 'as the active ingredient', only_one), ('contains', 'as the active ingredients', not only_one), ('active ingredient is', '', only_one)]
    for i in range(len(phrases)):
        act_srch = re.search(phrases[i], text)
        actv_substances = []
        if act_srch != None:
            last_one = False
            sentence = text[act_srch.start():act_srch.end()]
            begin_index = re.search(match[i][0], sentence).end()
            end_index = re.search(match[i][1], sentence).start()
            if match[i][1] == '':
                phrase_match = sentence[begin_index+1:]
            else:
                phrase_match = sentence[begin_index+1:end_index]
            phrase_match = phrase_match.replace("\n", "") # get rid of any new line symbols
            if phrase_match[-1] == " ":
                phrase_match = phrase_match[:-1]
            nlp = spacy.load('en') # load vocab
            words = phrase_match.split(" ")
            curr_actv_subst = ""
            for j in range(len(words)):
                is_end = False
                word = words[j]
                if word == 'and':
                    last_one = True
                if word[-1] in [',', ":", '.']:
                    word = word[:-1]
                    is_end = True
                if word not in nlp.vocab:
                    curr_actv_subst += word + " "
                else: # e.g. "active substance is rsodametal and this ...." consider end of referral to active subst
                    if curr_actv_subst != "":
                        is_end = True
                if is_end and curr_actv_subst != "":
                    curr_actv_subst = curr_actv_subst.strip()
                    actv_substances.append(curr_actv_subst)
                    curr_actv_subst = ""
                    if match[i][2] == only_one:
                        # print("match: " , match[i])
                        return actv_substances
                if (last_one and is_end) or (last_one and word not in nlp.vocab):
                    return actv_substances

            return actv_substances
    return "no match"



#
#
#
#
#
# active_substances = [get_active_subst(doc) for doc in docs]
# print(active_substances) # ['pancuronium bromide', None, None, 'gadoteridol', None]

# https://spacy.io/usage/linguistic-features#section-rule-based-matching
# spcy_sentence = nlp(u'' + sentence)
#  for token in spcy_sentence:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)


# IMPORTANT - EXTRACTING TEXT FROM THESE KIND OF LEAFLETS DOES NOT WORK WELL - HENCE NO MATCH FOR http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf.
# Uncomment line below to see what I mean
# print(docs[2]) # text extracted from pdf above
