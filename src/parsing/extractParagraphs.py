import re
import GParser, ClearXML
import xml.etree.ElementTree as ET

url = "http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1516338822280.pdf"
url2 = "http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1510895758237.pdf"

def extract_paragraphs(xml_string):
    root = ET.fromstring(xml_string + "</pages>")
    # print(root.tag)

    paragraphs = []

    # Compute average text size
    size_num = 0;
    text_num = 0;
    for text in root.iter("text"):
        size = text.get("size")
        if (size):
            size_num += float(text.get("size"))
            text_num += 1
    average_text_size = size_num/text_num

    # Compute average line width based on bboxes
    width_sum = 0
    line_num = 0
    for line in root.iter('textline'):
        bbox = line.get('bbox')
        params = bbox.split(',')
        width = float(params[2]) - float(params[0])
        line_num += 1
        width_sum += width
    average_line_width = width_sum / line_num


    current_paragraph = ""
    start_line = 0
    line_num = 0
    previous_line_font_size = 0

    for line in root.iter("textline"):
        line_text_size_sum = 0
        line_length = 0
        line_text= ""

        bbox = line.get('bbox')
        params = bbox.split(',')
        line_width = float(params[2]) - float(params[0])

        for text in line.iter("text"):
            size = text.get("size")
            if (size):
                line_text_size_sum += float(size)
                line_length += 1
                line_text += text.text

        line_font_size = line_text_size_sum/line_length if line_length > 0 else 0

        # Make a pragraph division
        if line_font_size > (previous_line_font_size + 2):
            # print(current_paragraph)
            paragraphs.append(current_paragraph)
            current_paragraph = ""

        # Delete whitespace at the beginning of the line
        line_text = re.sub(r'^\s*', '', line_text)

        if (line_font_size < (previous_line_font_size - 2)
                or re.match(r'^\s*•', line_text)
                or re.match(r'^\s*\d\.', line_text))\
                and not current_paragraph.endswith('\n'):
            line_text = "\n" + line_text

        if line_width < (average_line_width - 20):
            line_text += "\n"

        if not current_paragraph.endswith(' ') and not current_paragraph.endswith('\n') and not current_paragraph == '':
            current_paragraph += " "
        current_paragraph += line_text
        previous_line_font_size = line_font_size
        line_num += 1

    # print(paragraphs)
    return paragraphs


str = GParser.convert_pdf(url, format='xml')
file = open('sample_outputs/orginalXML.xml', 'w', encoding="utf8")
file.write(str)
extract_paragraphs(str)
str = ClearXML.clear_XML_from_text_tags(str)
file = open('sample_outputs/clearedXML.xml', 'w', encoding="utf8")
file.write(str)
