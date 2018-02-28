import parsing.GParser as Parser
import parsing.extractParagraphsLeaflet as extractParagraphsLeaflet
import parsing.extractParagraphsSPC as extractParagraphsSPC
import boto3
import xml.etree.ElementTree as ET
import urllib

# Get database resource
dynamodb = boto3.resource('dynamodb')
'''
# Create table for drugs data
table = dynamodb.create_table(
    TableName='drugs',
    KeySchema=[
        {
            'AttributeName': 'active_substance',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'product',
            'KeyType': 'RANGE'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'active_substance',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'product',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)
'''
csvTable = dynamodb.Table('csv_advice')
linksTable = dynamodb.Table('leaflet_links')
drugsTable = dynamodb.Table('drugs')

linksResponse = linksTable.scan()
csvResponse = csvTable.scan()

csvs = csvResponse['Items']
n=98
for drug in linksResponse['Items']:
    if n > 0:
        n = n - 1
        continue

    active_substance = drug['drug']
    data = drug['data']
    seen = []
    csv = {}

    for csv_ in csvs:
        name = csv_['drug']
        if (name.lower() in active_substance.lower() or active_substance.lower() in name.lower()):
            csv = csv_
            break

    for product in data:
        link = product['link']
        product_name = product['product']
        pdf_name = product['pdf_name']
        type = 'leaflet' if pdf_name.startswith('leaflet') else 'spc'

        if (product_name, type) in seen:
            continue

        print(active_substance)
        print(product_name)
        print(link)
        print(pdf_name)
        print()

        # Link to PDF expired
        try:
            xml = Parser.convert_pdf(link, format='xml')
        except urllib.error.HTTPError as e:
            continue
        except TypeError as e:
            continue

        if type == 'leaflet':
            # Characters in PDF with no representation in the encoding used by the XML parser, ignore
            try:
                paras = extractParagraphsLeaflet.extract_paragraphs(xml)
            except ET.ParseError as e:
                continue

            # PDF contains no embedded text
            if paras == []:
                continue

            if product_name in [t[0] for t in seen]:
                drugsTable.update_item(
                    Key={
                        'active_substance': active_substance,
                        'product': product_name
                    },
                    UpdateExpression='SET leaflet = :val1',
                    ExpressionAttributeValues={
                        ':val1': {
                            'link': link,
                            'pdf_name': pdf_name,
                            'paragraphs': paras
                        }
                    }
                )

            else:
                if csv:
                    drugsTable.put_item(
                        Item={
                            'active_substance': active_substance,
                            'product': product_name,
                            'csv': {
                                'title': csv['drug'],
                                'advice': csv['advice']
                            },
                            'leaflet': {
                                'link': link,
                                'pdf_name': pdf_name,
                                'paragraphs': paras
                            }
                        }
                    )

                else:
                    drugsTable.put_item(
                        Item={
                            'active_substance': active_substance,
                            'product': product_name,
                            'leaflet': {
                                'link': link,
                                'pdf_name': pdf_name,
                                'paragraphs': paras
                            }
                        }
                    )

        else:
            try:
                paras = extractParagraphsSPC.extract_paragraphs(xml)
            except ET.ParseError as e:
                continue

            if paras == []:
                continue

            if product_name in [t[0] for t in seen]:
                drugsTable.update_item(
                    Key={
                        'active_substance': active_substance,
                        'product': product_name
                    },
                    UpdateExpression='SET spc = :val1',
                    ExpressionAttributeValues={
                        ':val1': {
                            'link': link,
                            'pdf_name': pdf_name,
                            'paragraphs': paras
                        }
                    }
                )

            else:
                if csv:
                    drugsTable.put_item(
                        Item={
                            'active_substance': active_substance,
                            'product': product_name,
                            'csv': {
                                'title': csv['drug'],
                                'advice': csv['advice']
                            },
                            'spc': {
                                'link': link,
                                'pdf_name': pdf_name,
                                'paragraphs': paras
                            }
                        }
                    )

                else:
                    drugsTable.put_item(
                        Item={
                            'active_substance': active_substance,
                            'product': product_name,
                            'spc': {
                                'link': link,
                                'pdf_name': pdf_name,
                                'paragraphs': paras
                            }
                        }
                    )

        seen.append((product_name, type))

