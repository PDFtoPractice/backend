import GParser as GParser
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
            last_one = False
            sentence = text[act_srch.start():act_srch.end()]
            begin_index = re.search(match[i][0], sentence).end()
            end_index = re.search(match[i][1], sentence).start()
            if match[i][1] == '':
                phrase_match = sentence[begin_index+1:]
            else:
                phrase_match = sentence[begin_index+1:end_index]
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


def get_med_for(para, nlp): # extract purpose e.g. 'stop blood clot' -> 'medicine to stop blood clot' 'medicine to help to stop blood clots'
    from spacy.lemmatizer import Lemmatizer
    purpose = []
    phrases = ['help to[\w\s]+.', 'helps to[\w\s]+.', 'used to[\w\s]+.', 'used for[\w\s]+.']
    for phrase in phrases:
        srch = re.search(phrase, para)
        if srch != None:
            # analyse using spacy
            match = srch.group(0)
            seenFirstVerb = False
            doc = nlp(u'' + match)
            for i in range(len(doc)):
                token = doc[i]
                if token.pos_ == "VERB":
                    if seenFirstVerb:
                        span = doc[i:len(doc)]
                        break
                    else:
                        seenFirstVerb = True
            # get first occurance of noun in this span. stop phrase there and add to purpose
            # if following noun we have ADP (i.e. 'in', 'on'), take noun following ADP and append to built up phrase so far and append to purpose
            index = -1 # index of ADP
            purpose1 = ''
            lemmas = []
            for i in range(len(span)):
                token = span[i]
                if token.pos_ == "NOUN":
                    if i!=(len(span)-1) and span[i+1].pos_ != "NOUN":
                        purpose1 = span[:i+1]
                        for lemma in lemmas:
                            purpose1txt = purpose1.text
                            purpose1 = purpose1txt.replace(lemma[0], lemma[1])
                        purpose.append(purpose1)
                        if (len(span)-1) != i and span[i+1].pos_ == "ADP":
                            index = i+1
                        break
                elif token.pos_ == "VERB":
                    lemma = (token.text, token.lemma_)
                    lemmas.append(lemma)

            if index != -1:
                for j in range(index, len(span)):
                    token = span[j]
                    if token.pos_ == "NOUN" and span[j+1].pos_ != "NOUN":
                        purpose2 = span[:j+1]
                        purpose.append(purpose2.text)

            sz = len(purpose)
            for i in range(sz):
                item = purpose[i]
                new_item = 'medicine to ' + item
                purpose.append(new_item)
            return purpose
    return purpose


# receives url of spcpil drug leaflet, returns lists of purposes for the drug if any can be found, otherwise returns empty list
# Like http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1440737849470.pdf
def get_purpose(paras, nlp):
    heading_matches = ['What[\w\s]+are and what they are used for.', 'What[\w\s]+is and what it is used for']
    groups_matches = [('[\w\s] belongs to a group of medicines called [\'|\‘|\"|\‘][\w\s|-]+[\'|\‘|\"|\'],*[\w\s]+', '[\w\s] belongs to a group of medicines called'), ('[\w\s] belongs to a group of medicines called[\w\s].', '[\w\s] belongs to a group of medicines called'), ('[\w\s]+ belongs to a group of medicines known as [\w\s]+.', '[\w\s]+ belongs to a group of medicines known as')]
    group = []
    purpose = ''
    for para in paras:
        para = para.replace("\n", "")  # get rid of any new line symbols that mess up the search
        for heading in heading_matches: # get relevant paragraph
            srch = re.search(heading, para)
            if srch != None:
                for phrase_pair in groups_matches:
                    sentence = re.search(phrase_pair[0], para)
                    if sentence != None:
                        sentence =sentence.group(0)
                        sentence = re.sub(phrase_pair[1], '', sentence)

                        doc_sentence = nlp(u'' + sentence)
                        curr_group = ''
                        for tok in doc_sentence:
                            if tok.text in ['\'', '"', '‘']:
                                continue
                            elif tok.is_stop or (tok.is_punct and tok.text != '-'):
                                curr_group = curr_group.strip()
                                break
                            else:
                                curr_group += tok.text + ' '
                        curr_group = re.sub(' - ', '-', curr_group)
                        if curr_group != '':
                            group.append(curr_group)
                            if curr_group[-1] == 's':
                                group.append(curr_group[:-1])
                            search_hyphen = re.search('-', curr_group)
                            if search_hyphen != None: # if contains hyphen between words, add aliases
                                group.append(re.sub('-', ' ', curr_group))
                                group.append(re.sub('-', '', curr_group))
                        sentence = re.sub(curr_group, '', sentence).strip()

                        purpose_srch = sentence
                        purpose = get_med_for(para, nlp)
                        return group, purpose

                # extract purpose e.g. 'medicine to help stop blood clots'
                stop_synonyms = ['stop', 'prevent', 'inhibit']



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
    common_title = re.search('Before you take[\w\s]+\n', text)
    if common_title != None:
        common_title = common_title.group(0)
        common_title = re.sub('Before you take ', '', common_title)
        if(common_title.endswith('Tablets')):
            aliases.append(common_title.replace('Tablets', '').strip()) # check this works
        aliases.append(common_title)

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
    if group_of_meds != []:
        aliases += group_of_meds
    if purpose != '':
        aliases.append(purpose)
    return aliases

def conflicting_conditions(paras, nlp):
    # loop through paras and get bit with if... if ... if ... bullet points
    # do clean up
    conditions = []
    bullet_pts = []
    for bullet_pt in bullet_pts:
        # analyse structure of phrases and extract relevant bit, append to
        cond = ''
        if cond != '':
            conditions.append(cond)

    return conditions



def test_aliases():
    # text = GParser.convert_pdf(url, format='text')
    urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1516338822280.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1440737849470.pdf']
    correct_group = [['antithrombotics', 'antithrombotic'], ['anti-thrombotic agents', 'anti-thrombotic agent', 'anti thrombotic agents', 'antithrombotic agents']]
    correct_purpose = ['prevent blood clots', 'stop blood clots forming']
    nlp = spacy.load('en')  # load vocab
    for i in range(len(urls)):
        xmldoc = GParser.convert_pdf(urls[i], format='xml')
        paras = ExtractParasLflt.extract_paragraphs(xmldoc)
        text = GParser.convert_pdf(urls[i], format='text')
        group_of_meds, purpose = get_purpose(paras, nlp)
        # print(group_of_meds)
        # print(purpose)
        # print (group_of_meds == correct_group[i])
        # print (purpose == correct_purpose[i])
        print(get_aliases(urls[i], ''))
        # print(get_active_subst(text, nlp))

# test_aliases()



def test_extract_purpose():
    txt = ['and binds to proteins in your blood to help to prevent blood clots.', 'and binds to proteins in your blood to help to prevent blood clots in the brain.', 'and is used to prevent blood clots.', 'and is used to decrease blood pressure.', 'and is used to decrease blood pressure and alleviate chest pain.', 'used for preventing blood clots.']
    nlp = spacy.load('en')  # load vocab
    for t in txt:
        print(t)
        purpose = get_med_for(t, nlp)
        print(purpose)

test_extract_purpose()
# url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1440737849470.pdf'
# url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515129004813.pdf'
# url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1450423174307.pdf'
# url = 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1516338822280.pdf'
