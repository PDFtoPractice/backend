import GParser
import ClearXML
import extractParagraphs as ExtractParas
import re
import spacy
nlp = spacy.load('en')
urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492496435313.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510292397494.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1517548373003.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515735504413.pdf']
docs = [GParser.convert_pdf(url, format='xml') for url in urls]
docs = [ExtractParas.extract_paragraphs(parsed) for parsed in docs]

# extract headings paras
headings = ['1. What (\s)+ is and what is is used for', '2. What you need to know before you are given ProHance', '3. How you are given (\s)+', '4. Possible side effects', '5. How to store [\s]+', '6. Further Information']

# rest need to fill
def get_active_subst(paras): # pass in paras for a drug's leaflet
    # print(docs[0])
    for para in paras:
        phrases = ['active substance is[\w\s]+.', 'active substances are [\w\s]+.', 'contains [\w]+ as the active ingredient', 'contains[\w]+ as the active ingredients']
        match = [('active substance is', ''), ('active substances are', ''), ('contains', 'as the active ingredient'), ('contains', 'as the active ingredients')]
        for i in range(len(phrases)):
            act_srch = re.search(phrases[i], para)
            if act_srch != None:
                sentence = para[act_srch.start():act_srch.end()]
                spcy_sentence = nlp(u'' + sentence)
                for token in spcy_sentence:
                    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)
                begin_index = re.search(match[i][0], sentence).end()
                end_index = re.search(match[i][1], sentence).start()
                if(match[i][1] == ''):
                    active_subst = sentence[begin_index+1:]
                else:
                    active_subst = sentence[begin_index+1:end_index]
                if active_subst[-1] == " ":
                    active_subst = active_subst[:-1]
                phrase = active_subst
                active_subst = ""
                for word in phrase.split(" "):
                    if word[-1] in [',', ":", '.']:
                        word = word[:-1]
                    nlp_word = nlp.vocab.strings[word]
                    if word not in nlp.vocab: # ugly hack - probably a better rule we can use
                        active_subst += word + " "
                return active_subst.strip()


# TODO: The other ingredients are: in 4th
active_substances = [get_active_subst(doc) for doc in docs]
print(active_substances) # ['pancuronium bromide', None, None, 'gadoteridol', None]

# https://spacy.io/usage/linguistic-features#section-rule-based-matching