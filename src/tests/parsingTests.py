import parsing.entityRecog as EntityRecog
import parsing.ClearXML as ClearXML
import parsing.GParser as GParser
import parsing.extractParagraphs as ExtractParas

def test_get_active_substance():
    urls = ['http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492496435313.pdf',
            'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510292397494.pdf',
            'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1512713289515.pdf',
            'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1517548373003.pdf',
            'http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1515735504413.pdf']
    docs = [GParser.convert_pdf(url, format='xml') for url in urls]

    active_substances = [EntityRecog.get_active_subst(doc) for doc in docs]
    print(EntityRecog.get_active_substance("The active substance is tafluprost. 1 ml") == "tafluprost")

