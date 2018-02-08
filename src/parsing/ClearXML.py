import re

file = "sample_outputs/testfile.txt"

def clear_XML(file):
    fp = open(file, encoding="utf8")
    text = fp.read()
    new_text = re.sub(r'<text .*>(.*)</text>\n', r'\1', text)
    new_text = re.sub(r'<text>\n</text>\n', '', new_text)
    new_text = re.sub(r'(<textline .*">)\n', r'\1', new_text)
    return new_text

str = clear_XML(file)
file = open('sample_outputs/clearedXML.txt', 'w', encoding="utf8")
file.write(str)
