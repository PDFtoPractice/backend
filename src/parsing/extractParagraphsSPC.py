import re
import GParser, ClearXML
import xml.etree.ElementTree as ET


def extract_paragraphs(xml_string):
    xml_string = re.sub(r'^', ' ', xml_string)
    root = ET.fromstring(xml_string + "</pages>")
    try:
        root = ET.fromstring(xml_string + "</pages>")
    except ET.ParseError as e:
        return []

    paragraphs = []

    # Delete numbering which gets out of order
    for text_box in root.iter("textbox"):
        for line in text_box.findall("textline"):
            bbox = line.get('bbox')
            params = bbox.split(',')
            if float(params[2]) < 120:
                text_box.remove(line)

    # Compute average line width based on bboxes
    width_sum = 0
    line_num = 0
    for line in root.iter('textline'):
        bbox = line.get('bbox')
        params = bbox.split(',')
        width = float(params[2]) - float(params[0])
        line_num += 1
        width_sum += width

    # Case of empty file (no embedded text in leaflet)
    if line_num == 0:
        return []

    average_line_width = width_sum / line_num

    current_paragraph = ""
    start_line = 0
    line_num = 0
    previous_line_font_size = 0
    previous_line_text = ''
    bold = False
    previous_bold = False
    line_bold = False
    previous_line_bold = False

    for line in root.iter("textline"):
        line_text_size_sum = 0
        line_length = 0
        line_text = ""

        bbox = line.get('bbox')
        params = bbox.split(',')
        line_width = float(params[2]) - float(params[0])

        previous_line_bold = line_bold
        line_bold = True
        bold = False
        for text in line.iter("text"):
            # Get the character font size
            size = text.get("size")
            if size:
                line_text_size_sum += float(size)
                line_length += 1

            # Get the character font name
            font = text.get("font")
            if font and text.text.isalpha():
                previous_bold = bold
                if "Bold" in font \
                        or "bold" in font\
                        or "Bd" in font:
                    bold = True
                else:
                    bold = False
                    if text.text.isalpha():
                        line_bold = False
                if not previous_bold and bold:
                    line_text += "<b>"
                if previous_bold and not bold:
                    line_text += "</b>"

            line_text += text.text      # Append text to the line

        if len(line_text) < 5:
            line_bold = False

        if bold:
            line_text += "</b>"     # If the last character was bold add closing tag

        line_font_size = line_text_size_sum/line_length if line_length > 0 else 0

        # Delete whitespace at the beginning and end of the line
        line_text = re.sub(r'^\s*', '', line_text)
        line_text = re.sub(r'\s*$', '', line_text)

        # Unify all the bullet point characters
        line_text = re.sub(r'^\(cid:127\)', '-', line_text)
        line_text = re.sub(r'^•', '-', line_text)
        line_text = re.sub(r'^–', '-', line_text)
        line_text = re.sub(r'^', '-', line_text)
        line_text = re.sub(r'^', '-', line_text)
        line_text = re.sub(r'^', '-', line_text)

        # Fix weird character coding
        line_text = re.sub(r'ﬂ\s?', r"fl", line_text)
        line_text = re.sub(r'ﬁ\s?', r"fi", line_text)
        line_text = re.sub(r'ﬀ\s?', r"ff", line_text)
        line_text = re.sub(r'’', r"'", line_text)

        # Make a paragraph division
        if ((line_font_size > (previous_line_font_size + 2)   # Increase in font size
                or re.match(r'^\s*$', previous_line_text)     # Previous line contained only whitespaces
                or (not previous_line_bold and line_bold))    # Previous line wasn't bold and current is
                and len(current_paragraph) > 60               # Each paragraph should have at least 60 chars
                and not re.match(r'^-', line_text)
                and not re.match(r':\s*(<.*>)*$', current_paragraph)):
            current_paragraph = re.sub(r'</b>\s*<b>', '', current_paragraph)
            current_paragraph = re.sub(r'^(<br>)*', '', current_paragraph)
            if len(current_paragraph) == 0:
                current_paragraph = "<br>"
            paragraphs.append(current_paragraph)
            # print("--------------\n" + current_paragraph)
            current_paragraph = ""

        # Insert line break before the line
        if ((line_font_size < (previous_line_font_size - 2)     # Decrease in font size
                or re.match(r'^-', line_text)                   # Line starts with bullet / dash
                or re.match(r'^\d\.', line_text)                # Line starts with digit e.g. 2.
                or previous_line_bold and not line_bold)        # Previous line was bold
                and not current_paragraph.endswith('<br>')):    # There is no line break already
            line_text = "<br>" + line_text

        # Insert line break after the line
        if (line_width < (average_line_width - 20)          # Line explicitly made shorter
                or re.match(r'^.*:\s*$', line_text)):       # Line ends with colon
            line_text += "<br>"


        # Add line to the current paragraph
        if not current_paragraph.endswith(' ') and not current_paragraph.endswith('<br>') and not current_paragraph == '':
            current_paragraph += " "
        current_paragraph += line_text
        previous_line_text = line_text
        previous_line_font_size = line_font_size
        line_num += 1

    current_paragraph = re.sub(r'^(<br>)*', '', current_paragraph)
    current_paragraph = re.sub(r'</b>\s*<b>', '', current_paragraph)

    # Add the last paragraph
    if (not re.match(r'^(\s*\n*)*$', current_paragraph)) and len(current_paragraph) > 5:
        paragraphs.append(current_paragraph)

    if "" in paragraphs:
        paragraphs.remove("")

    return paragraphs


url1 = "http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1492497354844.pdf"  # spc for doctor
url2 = "http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1475211116165.pdf"
url3 = "http://www.mhra.gov.uk/home/groups/spcpil/documents/spcpil/con1514526226656.pdf" # Welfairin


def test_url(url, sentence):
    str = GParser.convert_pdf(url, format='xml')
    file = open('sample_outputs/orginalXML.xml', 'w', encoding="utf8")
    file.write(str)
    paragraphs = extract_paragraphs(str)
    html = ""
    contains_sentence = False
    for text in paragraphs:
        html += text
        html += "<br>---------<br>\n"
        if sentence in text:
            contains_sentence = True
    file = open('sample_outputs/paragraphs.html', 'w', encoding="utf8")
    file.write(html)
    assert contains_sentence


def test_answer():
    test_url(url1, "Interaction with other medicinal products and other forms of interaction")
    test_url(url2, "Interaction with other medicinal products and other forms of interaction")


test_url(url3, "")
