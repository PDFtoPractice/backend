import src.paragraph_extraction.parsing.GParser as GParser
import src.paragraph_extraction.extraction.extractParagraphsLeaflet as ExtractParasLflt

import re
import spacy
from collections import OrderedDict


# urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492496435313.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510292397494.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1517548373003.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515735504413.pdf']
# docs = [convert_pdf(url, format='text') for url in urls]


# extract headings paras
headings = ['1. What (\s)+ is and what it is used for', '2. What you need to know before you are given ProHance', '3. How you are given (\s)+', '4. Possible side effects', '5. How to store [\s]+', '6. Further Information']

# receives text of drug leaflet, returns list of active substances if any can be found otherwise returns empty list
def get_active_subst(text, nlp):
    only_one = True    # whether there are more than one active substance to extract
    phrases = ['active substance is[\w\s]+.', 'active substances are([\w\s][,]*)+.', 'contains[\w\s]+ as the active ingredient', 'contains[\w]+ as the active ingredients', 'active ingredient is[\w\s]+.', 'contains[\w\s|.]+ of the active substance', 'The active ingredient,[\w\s]+, is', '[\w\s]+ \(active ingredient\)', 'contains the active substance[\w\s]+', 'contains the active substances[\w\s]+', 'contains the active ingredient[\w\s]+', 'contains the active ingredients[\w\s]+']
    match = [('active substance is', '', only_one), ('active substances are', '', not only_one), ('contains', 'as the active ingredient', only_one), ('contains', 'as the active ingredients', not only_one), ('active ingredient is', '', only_one), ('contains', 'of the active substance', only_one), ('The active ingredient,', ', is', only_one), ('', '\(active ingredient\)', only_one), ('contains the active substance', '', only_one), ('contains the active substances', '', not only_one),  ('contains the active ingredient', '', only_one), ('contains the active ingredients', '', not only_one)]
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
                    if word == words[len(words)-1]: # if last word is active substance word, append to curr_actv_subst
                        curr_actv_subst = curr_actv_subst.strip()
                        actv_substances.append(curr_actv_subst.lower())
                else: # e.g. "active substance is rsodametal and this ...." consider end of referral to active subst
                    if curr_actv_subst != "":
                        is_end = True
                if is_end and curr_actv_subst != "":
                    curr_actv_subst = curr_actv_subst.strip()
                    actv_substances.append(curr_actv_subst.lower())
                    curr_actv_subst = ""
                    if match[i][2] == only_one:
                        # print("match: " , match[i])
                        return actv_substances
                if (last_one and is_end) or (last_one and word not in nlp.vocab):
                    return actv_substances
            actv_substances = list(dict((x, True) for x in actv_substances).keys())
            return actv_substances
    return []

# deal with Topical corticosteroids are able to reduce the inflammation caused by a variety of skin condition
def get_med_for(para, nlp): # extract purpose e.g. 'stop blood clot' -> 'medicine to stop blood clot' 'medicine to help to stop blood clots'
    purposes = []
    phrases = ['help to[\w\s]+.', 'helps to[\w\s]+.', 'used to[\w\s]+.', 'used for[\w\s]+.', 'are able to[\w\s]+', 'is able to[\w\s]+']
    for phrase in phrases:
        srch = re.search(phrase, para)
        if srch != None:
            # analyse using spacy
            match = srch.group(0)
            if re.search('not', match) == None: # deal with should not situation
                seenFirstVerb = False
                doc = nlp(u'' + match)
                span = None
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
                purpose = ''
                lemmas = []
                if span != None:
                    for i in range(len(span)):
                        token = span[i]
                        if token.pos_ == "NOUN":
                            if i!=(len(span)-1) and span[i+1].pos_ != "NOUN":
                                purpose = span[:i+1]
                                for lemma in lemmas:
                                    if not isinstance(purpose, str):
                                        purpose = purpose.text
                                    if purpose.lower() not in ['treat the following conditions']:
                                        purposes.append(purpose)
                                        if lemma[0] != lemma[1]:
                                            non_lemmatized = 'medicines for ' + purpose
                                            purposes.append(non_lemmatized)
                                            purpose = purpose.replace(lemma[0], lemma[1])
                                            purposes.append(purpose)
                                            lemmatized = 'medicine to ' + purpose
                                            purposes.append(lemmatized)
                                        else:
                                            purposes.append(purpose)
                                            purpose = 'medicine to ' + purpose
                                            purposes.append(purpose)
                                if purpose.lower() not in ['treat the following conditions']:
                                    purposes.append(purpose.lower())
                                    if (len(span)-1) != i and span[i+1].pos_ == "ADP":
                                        index = i+1
                                    break
                        elif token.pos_ == "VERB":
                            lemma = (token.text.lower(), token.lemma_.lower())
                            lemmas.append(lemma)
                    if index != -1:
                        for j in range(index, len(span)):
                            token = span[j]
                            if token.pos_ == "NOUN" and span[j+1].pos_ != "NOUN":
                                purpose2 = span[:j+1]
                                purposes.append(purpose2.text.lower())
                                purposes.append('medicine to ' + purpose2.text.lower())
                    return purposes
    return purposes


# receives spcpil url of drug leaflet and returns aliases
# what order do we want for most efficient search results?
# https://spacy.io/usage/linguistic-features
# call function for all relevant leaflets under drug name
def get_aliases(url):
    nlp = spacy.load('en')  # load vocab
    text = GParser.convert_pdf(url, format='text')
    xmldoc = GParser.convert_pdf(url, format='xml')
    paras = ExtractParasLflt.extract_paragraphs(xmldoc)
    aliases = []
    common_title = re.search('Before you take[\w\s]+\n', text)
    if common_title != None:
        common_title = common_title.group(0)
        common_title = re.sub('Before you take ', '', common_title)
        common_title = re.sub('\n', '', common_title)
        common_title = re.sub('•', '', common_title)
        common_title = common_title.strip()
        if(common_title.endswith('Tablets')):
            aliases.append(common_title.replace('Tablets', '').strip().lower()) # check this works
        aliases.append(common_title.lower())
    actv_subs = get_active_subst(text, nlp)

    if actv_subs != []:
        for active_sub in actv_subs:
            aliases.append(active_sub.lower())

    # get purpose and get group of medicines it belongs to
    heading_matches = [('What[\w\s]+are and what they are used for', 'What', 'are and what they are used for' ), ('What[\w\s]+is and what it is used for', 'What', 'is and what it is used for' )]
    groups_matches = [('[\w\s]+ group of medicines called [\w\s]+-*[\w\s]+', '[\w\s]+ group of medicines called'), ('[\w\s]+ group of medicine called [\w\s]+-*[\w\s]+', '[\w\s]+ group of medicine called'), ('[\w\s] belongs to a group of medicines called [\'|\‘|\"|\‘][\w\s]+-*[\w\s]+[\'|\‘|\"|\'],*[\w\s]+', '[\w\s] belongs to a group of medicines called'), ('[\w\s] belongs to a group of medicines called[\w\s]+-*[\w\s]+.', '[\w\s] belongs to a group of medicines called'), ('[\w\s]+ group of medicines known as [\w\s]+-*[\w\s]+.', '[\w\s]+ group of medicines known as')]
    group = []
    purposes = []
    for para in paras:
        para = para.replace("\n", "")  # get rid of any new line symbols that mess up the search
        for heading in heading_matches: # get relevant paragraph
            srch = re.search(heading[0], para)
            if srch != None:
                title = srch.group(0)
                if title.count("\n") >= 3:
                    continue
                title = re.sub(heading[1], '', title)
                title = re.sub(heading[2], '', title)
                title = re.sub('\n', '', title)
                title = re.sub('•', '', title)
                title = title.strip()
                if title != '':
                    aliases.append(title.lower())
                    if (not title.endswith('Tablets')) and (not title.endswith('tablets')):
                        title = title + ' ' + 'tablets'
                        aliases.append(title.lower())
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
                            elif tok.is_stop or (tok.is_punct and (tok.text != '-')):
                                curr_group = curr_group.strip()
                                break
                            else:
                                curr_group += tok.text + ' '
                        curr_group = re.sub(' - ', '-', curr_group)
                        curr_group = curr_group.strip()
                        if curr_group != '':
                            group.append(curr_group.lower())
                            if curr_group[-1] == 's':
                                group.append(curr_group[:-1].lower())
                            search_hyphen = re.search('-', curr_group)
                            if search_hyphen != None: # if contains hyphen between words, add aliases
                                group.append(re.sub('-', ' ', curr_group).lower())
                                group.append(re.sub('-', '', curr_group).lower())
                        sentence = re.sub(curr_group, '', sentence).strip()
        if purposes == []:
            purpose = get_med_for(para, nlp)
            if purpose != []:
                purposes += purpose

    group_of_meds = group
    aliases = list(dict((alias, True) for alias in aliases).keys())
    group_of_meds = list(dict((g, True) for g in group_of_meds).keys())
    purposes = list(dict((p, True) for p in purposes).keys())

    return aliases, group_of_meds, purposes



def test_aliases():
    # text = GParser.convert_pdf(url, format='text')
    urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1516338822280.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1440737849470.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1487918987625.pdf', 'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1471582099226.pdf']
    correct_aliases = [['abciximab', 'reopro', 'reopro tablets'],
                       ['persantin tabletshow to take persantin tabletspossible side effects   how to store persantin tabletsfurther information1what persantin tablets are and what they are used for', 'dipyridamole', 'persantin tablets', 'dipyridamol tablets'],
                        ['hydrocortisone butyrate', 'locoid', 'locoid tablets', 'hydrocortisone', 'hydrocortisone tablets'],
                        ['lidocaine']]

    correct_group_of_meds = [['antithrombotics', 'antithrombotic'], ['anti-thrombotic agents', 'anti-thrombotic agent', 'anti thrombotic agents', 'antithrombotic agents'], [],[] ]
    correct_purposes = [['prevent blood clots', 'medicine to prevent blood clots'], ['take Persantin Tablets', 'medicine to take Persantin Tablets', 'medicine to take persantin tablets'], ['treat a variety', 'medicine to treat a variety', 'treat a variety of skin conditions', 'medicine to treat a variety of skin conditions', 'treat a variety of skin conditions such as eczema', 'medicine to treat a variety of skin conditions such as eczema', 'treat a variety of skin conditions such as eczema and dermatitis', 'medicine to treat a variety of skin conditions such as eczema and dermatitis'], ['relax muscles', 'medicine to relax muscles', 'relax muscles in general anaesthesia', 'medicine to relax muscles in general anaesthesia'] ]
    nlp = spacy.load('en')  # load vocab
    for i in range(len(urls)):
        xmldoc = GParser.convert_pdf(urls[i], format='xml')
        paras = ExtractParasLflt.extract_paragraphs(xmldoc)
        text = GParser.convert_pdf(urls[i], format='text')
        aliases, group_of_meds, purposes = get_aliases(urls[i])
        assert aliases == correct_aliases[i]
        assert group_of_meds == correct_group_of_meds[i]
        assert purposes == correct_purposes[i]




def test_extract_purpose():
    txt = ['and binds to proteins in your blood to help to prevent blood clots.', 'and binds to proteins in your blood to help to prevent blood clots in the brain.', 'and is used to prevent blood clots.', 'and is used to decrease blood pressure.', 'and is used to decrease blood pressure and alleviate chest pain.', 'used for preventing blood clots.']
    correct_purpose = [['prevent blood clots', 'prevent blood clots', 'medicine to prevent blood clots', 'medicine to prevent blood clots'],
                        ['prevent blood clots', 'prevent blood clots', 'medicine to prevent blood clots', 'medicine to prevent blood clots', 'prevent blood clots in the brain', 'medicine to prevent blood clots in the brain'],
                        ['prevent blood clots', 'prevent blood clots', 'medicine to prevent blood clots', 'medicine to prevent blood clots'],
                        ['decrease blood pressure', 'decrease blood pressure', 'medicine to decrease blood pressure', 'medicine to decrease blood pressure'],
                        ['decrease blood pressure', 'decrease blood pressure', 'medicine to decrease blood pressure', 'medicine to decrease blood pressure'],
                        ['preventing blood clots', 'medicines for preventing blood clots', 'prevent blood clots', 'medicine to prevent blood clots', 'prevent blood clots']
                        ]
    nlp = spacy.load('en')  # load vocab
    for i in range(len(txt)):
        purpose = get_med_for(txt[i], nlp)
        assert purpose == correct_purpose[i]

# test_extract_purpose()
# test_aliases()

