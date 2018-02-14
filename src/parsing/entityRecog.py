import GParser
import ClearXML
import extractParagraphs as ExtractParas
import re

urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492496435313.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510292397494.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1517548373003.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515735504413.pdf']

docs = []
for url in urls:
    str = GParser.convert_pdf(url, format='xml')
    paras = ExtractParas.extract_paragraphs(str)
    str = ClearXML.clear_XML_from_text_tags(str)
    docs.append(paras)

# extract headings paras
headings = ['1. What (\s)+ is and what is is used for', '2. What you need to know before you are given ProHance', '3. How you are given (\s)+', '4. Possible side effects', '5. How to store [\s]+', '6. Further Information']

# rest need to fill
def get_active_subst(paras): # pass in paras for a drug's leaflet
    # print(docs[0])
    for para in paras:
        start_index = -1
        search = re.search(headings[5].lower(), para.lower())
        if(search != None):
            start = search.start()
            relev_txt = para[start:]
            print("RELEVANT ACTIVE SUBSTANCE TEXT")

            phrases = ['active substance is [\s]+.', 'active substances are [\s].', 'contains [\s]+ as the active ingredient', 'contains [\s]+ as the active ingredients']
            for i in range(len(phrases)):
                act_match = re.match(phrases[i], relev_txt)
                if (act_match != None):
                    start = act_match.start()
                    end = act_match.end()
                    print(relev_txt[start:end])
                    break
                # closest_txt = relev_txt[actsub_index.end():]

            break

    # no match found in 6th section
    # search through rest of text for active substance, find closest mention of active substance

get_active_subst(docs[0])
