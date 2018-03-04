from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
from urllib import request

'''
convert_pdf(url, format='text', codec='utf-8', password='') parses the pdf found at the provided url into the format specified (text, html, xml) 
and outputs the parsed pdf as a string with the appropriate format
codec specifies the text encoding of the pdf, and password is the user password required to access the pdf (empty string if not required)
'''
def convert_pdf(url, format='text', codec='utf-8', password=''):
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams(line_overlap=0.5,
                 char_margin=2.0,
                 line_margin=0.9,
                 word_margin=0.5,
                 boxes_flow=0.5,
                 detect_vertical=False,
                 all_texts=False)
    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    remoteFile = request.urlopen(url).read()
    fp = BytesIO(remoteFile)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    return text
