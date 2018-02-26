from parsing import entityRecog as EntityRecog
from parsing import GParser

def test_get_active_substance():
    urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492496435313.pdf',
            'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510292397494.pdf',
            'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf',
            'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1517548373003.pdf',
            'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515735504413.pdf']
    docs = [GParser.convert_pdf(url, format='text') for url in urls]

    active_substances = [EntityRecog.get_active_subst(doc) for doc in docs]
    assert active_substances == ['pancuronium bromide', None, None, 'gadoteridol', None]

    assert EntityRecog.get_active_subst("The active substance is tafluprost. 1 ml") == ["tafluprost"]

    testtxt = "The active substances are rsodametal, georsf, and turoportin."
    testtxt2 = "The active substance is rsodametal and it is known for causing sdfsdf."  # what if it has 'and it is known for having side effects of <some stuff not in dictionary>. Say if count >= n of vocab words then assume end?
    testtxt3 = "The active substances are rsodametal, georsf, and turoportin, and they are known for causing sdfss."
    testtxt4 = "The active substances are rsodametal gaterol, georsf, and turoportin."
    testtxt5 = "The active substance is rsodametal gaterol."
    testtxt6 = "The active substance is rsodametal gaterol and it can cause extreme inflammation."
    testtxt7 = "The active substance is rsodametal gaterol and it can cause extreme sdfsdfs."

    assert EntityRecog.get_active_subst(testtxt) == ['rsodametal', 'georsf', 'turoportin']
    assert EntityRecog.get_active_subst(testtxt2) == ['rsodametal']
    assert EntityRecog.get_active_subst(testtxt3) == ['rsodametal',  'georsf', 'turoportin']
    assert EntityRecog.get_active_subst(testtxt4) == ['rsodametal gaterol', 'georsf', 'turoportin']
    assert EntityRecog.get_active_subst(testtxt5) == ['rsodametal gaterol']
    assert EntityRecog.get_active_subst(testtxt6) == ['rsodametal gaterol']
    assert EntityRecog.get_active_subst(testtxt7) == ['rsodametal gaterol']

