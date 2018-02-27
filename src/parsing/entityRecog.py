import GParser as GParser
# import extractParagraphs as ExtractParas
import extractParagraphsLeaflet as ExtractParasLflt

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
    phrases = ['active substance is[\w\s]+.', 'active substances are([\w\s][,]*)+.', 'contains[\w\s]+ as the active ingredient', 'contains[\w]+ as the active ingredients', 'active ingredient is[\w\s]+.', 'contains[\w\s|.]+ of the active substance', 'The active ingredient,[\w\s]+, is', '[\w\s]+ \(active ingredient\)']
    match = [('active substance is', '', only_one), ('active substances are', '', not only_one), ('contains', 'as the active ingredient', only_one), ('contains', 'as the active ingredients', not only_one), ('active ingredient is', '', only_one), ('contains', 'of the active substance', only_one), ('The active ingredient,', ', is', only_one), ('', '\(active ingredient\)', only_one)]
    for i in range(len(phrases)):
        act_srch = re.search(phrases[i], text)
        actv_substances = []
        if act_srch != None:
            print("Reached here")
            print(phrases[i])
            last_one = False
            sentence = text[act_srch.start():act_srch.end()]
            begin_index = re.search(match[i][0], sentence).end()
            end_index = re.search(match[i][1], sentence).start()
            if match[i][1] == '':
                phrase_match = sentence[begin_index+1:]
            else:
                phrase_match = sentence[begin_index+1:end_index]
            print(phrase_match)
            phrase_match = phrase_match.replace("\n", "") # get rid of any new line symbols
            phrase_match = phrase_match.strip()
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
                    print(curr_actv_subst)
                    if word == words[len(words)-1]: # if last word is active substance word, append to curr_actv_subst
                        curr_actv_subst = curr_actv_subst.strip()
                        actv_substances.append(curr_actv_subst)
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
    phrases = [('What[\w\s]+are and what they are used for.', 'This belongs to a group of medicines called[\w\s].'), ('What[\w\s]+is and what it is used for', 'This belongs to a group of medicines called[\w\s]')]
    aliases = []
    for para in paras:
        for heading in phrases:
            srch = re.search(heading[0], para)
            if srch != None:
                print("Reached here")
                txt = srch.group(0)
                print(txt)
                if re.search(heading[1], txt) != None:
                    print("OVER HERE")
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
# call function for all relevant leaflets under drug name
def get_aliases(url, product):
    nlp = spacy.load('en')  # load vocab
    text = GParser.convert_pdf(url, format='text')
    xmldoc = GParser.convert_pdf(url, format='xml')
    paras = ExtractParasLflt.extract_paragraphs(xmldoc)
    aliases = []

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
            title = re.sub('[ ]{2,}', ' ', title)  # replace multiple spaces by one space
            title = re.sub('\n', '', title)
            title = re.sub('®', '', title).strip()
            title = re.sub('<br>|<b>', '', title)
            title = re.sub('</br>|</b>', '', title)
            title = re.sub('\([\w]+\)', '', title)
            title = title.strip()
            aliases.append(title)
            if title.endswith('Tablets'):
                title.replace('Tablets', '')
                title.strip()
                dosage_srch = re.search('\d', title)
                if dosage_srch != None:
                    title = re.sub('<br>|<b>', '', title)
                    title = re.sub('</br>|</b>', '', title)
                    title = title[:dosage_srch.start()].strip()

                    aliases.append(title)
            break

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
    print("aliases" , aliases)
    return aliases


# print(docs[2]) # text extracted from pdf above
# url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1440737849470.pdf'
# url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515129004813.pdf'
# url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1450423174307.pdf'
url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1516338822280.pdf'
# get_aliases(url)

nlp = spacy.load('en')  # load vocab

xmldoc = GParser.convert_pdf(url, format='xml')
paras = ExtractParasLflt.extract_paragraphs(xmldoc)
# text = GParser.convert_pdf(url, format='text')

# print(get_active_subst(text, nlp))

group_of_meds, purpose = get_purpose(paras, nlp)
print("Group of meds ", group_of_meds)
print("Purpose ", purpose)
