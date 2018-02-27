import GParser as GParser
import extractParagraphs as ExtractParas
# import extractParagraphsLeaflet as ExtractParasLflt

# from parsing import GParser # testing import needed
import re
import spacy
urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492496435313.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510292397494.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1517548373003.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515735504413.pdf']
docs = [GParser.convert_pdf(url, format='text') for url in urls]


# extract headings paras
headings = ['1. What (\s)+ is and what it is used for', '2. What you need to know before you are given ProHance', '3. How you are given (\s)+', '4. Possible side effects', '5. How to store [\s]+', '6. Further Information']

# receives text of drug leaflet, returns list of active substances if any can be found otherwise returns empty list
def get_active_subst(text, nlp):
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
    return []

# receives url of spcpil drug leaflet, returns lists of purposes for the drug if any can be found, otherwise returns empty list
# Like http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1440737849470.pdf
def get_purpose(paras, nlp):
    heading_matches = ['What[\w\s]+are and what they are used for.', 'What[\w\s]+is and what it is used for']
    phrases = [('What[\w\s]+are and what they are used for.', 'This belongs to a group of medicines called[\w\s].'), ('What[\w\s]+is and what it is used for', 'This belongs to a group of medicines called')]
    aliases = []
    for para in paras:
        for heading in phrases:
            srch = re.search(heading[0], para)
            if srch != None:
                txt = srch.group(0)
                if re.search(heading[1], txt) != None:
                    print(para)
                    str = re.sub(heading[1], '', srch.group(0)).strip()
                    print(str)
                    group = ''
                    doc = nlp(u'' + str)
                # for token in doc:
                #     if str(token)[-1] in [',', ":", '.']:
                #         token = token[:-1]
                #         group += ' ' + token
                #         group = group.strip()
                #         break
                #     elif token.dep_ == 'oprd':
                #         group += ' ' + token
                #         group = group.strip()
                #         break
                #     else:
                #         group += ' ' + token
                    print("Group ", group)

                    purpose = ''
                    return group, purpose

    return '', ''



# receives spcpil url of drug leaflet and returns aliases
# what order do we want for most efficient search results?
# https://spacy.io/usage/linguistic-features
def get_aliases(url):
    nlp = spacy.load('en')  # load vocab
    text = GParser.convert_pdf(url, format='text')
    xmldoc = GParser.convert_pdf(url, format='xml')
    paras = ExtractParas.extract_paragraphs(xmldoc)
    aliases = []
    print("aliases" , aliases)

    # common_title = re.search('Before you take[\w\s]+\n', text)
    # if common_title != None:
    #     common_title = common_title.group(0)
    #     common_title = re.sub('Before you take ', '', common_title)
    #     if(common_title.endswith('Tablets')):
    #         print(common_title)
    #         aliases.append(common_title.replace('Tablets', '').strip()) # check this works
    #     aliases.append(common_title)

    for para in paras:
        if para != '':
            title = para
            break

    title = re.sub('[ ]{2,}', ' ', title)  # replace multiple spaces by one space
    title = re.sub('\n', '', title)
    title = re.sub('®', '', title).strip()
    aliases.append(title)
    if title.endswith('Tablets'):
        title.replace('Tablets', '')
        title.strip()
        dosage_srch = re.search('\d', title)
        if dosage_srch != None:
            title = title[:dosage_srch.start()].strip()
            aliases.append(title)
    actv_subs = get_active_subst(text, nlp)
    if actv_subs != []:
        for active_sub in actv_subs:
            aliases.append(active_sub)

    # get purpose and get group of medicines it belongs to
    group_of_meds, purpose = get_purpose(paras, nlp)
    if group_of_meds != '':
        aliases.append(group_of_meds)
    if purpose != '':
        aliases.append(purpose)
    return aliases

# IMPORTANT - EXTRACTING TEXT FROM THESE KIND OF LEAFLETS DOES NOT WORK WELL - HENCE NO MATCH FOR http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf.
# Uncomment line below to see what I mean
# print(docs[2]) # text extracted from pdf above
url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1440737849470.pdf'
get_aliases(url)

nlp = spacy.load('en')  # load vocab
#
# doc = nlp(u'Naramig tablets contain naratriptan (hydrochloride), which belongs to a group of medicines called triptan exerme also known as 5-HT1 receptor agonists.')
#
# for token in doc:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#           token.shape_, token.is_alpha, token.is_stop)
xmldoc = GParser.convert_pdf(url, format='xml')
paras = ExtractParas.extract_paragraphs(xmldoc)
group_of_meds, purpose = get_purpose(paras, nlp)
