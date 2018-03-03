import re
import GParser as GParser

url = "http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1516338822280.pdf"
url2 = "http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510895758237.pdf"

def clear_XML_from_text_tags(text):
    new_text = re.sub(r'<text .*>(.*)</text>\n', r'\1', text)
    new_text = re.sub(r'<text>\n</text>\n', '', new_text)
    new_text = re.sub(r'<text> </text>\n', '', new_text)
    new_text = re.sub(r'(<textline .*">)\n', r'\1', new_text)
    return new_text


str = GParser.convert_pdf(url, format='xml')
str = clear_XML_from_text_tags(str)
file = open('sample_outputs/clearedXML.xml', 'w', encoding="utf8")
file.write(str)
