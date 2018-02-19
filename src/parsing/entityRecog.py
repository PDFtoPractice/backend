import GParser as GParser
import ClearXML as ClearXML
import extractParagraphs as ExtractParas
import re
import spacy
urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492496435313.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510292397494.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1517548373003.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515735504413.pdf']
docs = [GParser.convert_pdf(url, format='text') for url in urls]
paras = [ExtractParas.extract_paragraphs(parsed) for parsed in docs]

# extract headings paras
headings = ['1. What (\s)+ is and what is is used for', '2. What you need to know before you are given ProHance', '3. How you are given (\s)+', '4. Possible side effects', '5. How to store [\s]+', '6. Further Information']

# rest need to fill
def get_active_subst(text): # pass in paras for a drug's leaflet
        phrases = ['active substance is[\w\s]+.', 'active substances are[\w\s]+.', 'contains[\w\s]+ as the active ingredient', 'contains[\w]+ as the active ingredients', 'active ingredient is[\w\s]+.']
        match = [('active substance is', ''), ('active substances are', ''), ('contains', 'as the active ingredient'), ('contains', 'as the active ingredients'), ('active ingredient is', '')]
        for i in range(len(phrases)):
            act_srch = re.search(phrases[i], text)
            # print(act_srch)
            if act_srch != None:
                print(act_srch)
                sentence = text[act_srch.start():act_srch.end()]
                begin_index = re.search(match[i][0], sentence).end()
                end_index = re.search(match[i][1], sentence).start()
                if(match[i][1] == ''):
                    active_subst = sentence[begin_index+1:]
                else:
                    active_subst = sentence[begin_index+1:end_index]
                active_subst = active_subst.replace("\n", "") # get rid of any new line symbols
                if active_subst[-1] == " ":
                    active_subst = active_subst[:-1]
                phrase = active_subst
                active_subst = ""
                nlp = spacy.load('en') # load vocab
                for word in phrase.split(" "):
                    if word[-1] in [',', ":", '.']:
                        word = word[:-1]
                    nlp_word = nlp.vocab.strings[word]
                    if word not in nlp.vocab: # ugly hack - probably a better rule we can use
                        active_subst += word + " "
                return active_subst.strip()
        return "no match"


# active_substances = [get_active_subst(doc) for doc in docs]
# print(active_substances) # ['pancuronium bromide', None, None, 'gadoteridol', None]

# https://spacy.io/usage/linguistic-features#section-rule-based-matching
# spcy_sentence = nlp(u'' + sentence)
#  for token in spcy_sentence:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)


# IMPORTANT - EXTRACTING TEXT FROM THESE KIND OF LEAFLETS DOES NOT WORK WELL - HENCE NO MATCH FOR http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf.
# Uncomment line below to see what I mean
# print(docs[2]) # text extracted from pdf above
