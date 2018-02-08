from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO, BytesIO
from urllib import request

url = "http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1516338822280.pdf"

def convert_pdf_to_txt(url):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    remoteFile = request.urlopen(url).read()
    fp = BytesIO(remoteFile)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

def write_to_file(str):
    file = open('sample_outputs/testfile.txt', 'w')
    file.write(str)

str = convert_pdf_to_txt(url)
write_to_file(str)