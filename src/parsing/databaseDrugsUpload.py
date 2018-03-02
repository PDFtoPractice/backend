import parsing.GParser as Parser
import parsing.extractParagraphsLeaflet as extractParagraphsLeaflet
import parsing.extractParagraphsSPC as extractParagraphsSPC
import boto3
import urllib
from botocore.exceptions import ClientError
import time
import pdfminer.psparser as PE

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

n=0
not_seen = True

while 'LastEvaluatedKey' in linksResponse:
    linksResponse = linksTable.scan(
        ExclusiveStartKey=linksResponse['LastEvaluatedKey']
        )

    for drug in linksResponse['Items']:
        active_substance = drug['drug']
        n = n + 1

        if not_seen and active_substance != 'LAMOTRIGINE':
            continue
        not_seen = False

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
            type = 'leaflet' if pdf_name.startswith('leaflet') else 'spc' if pdf_name.startswith('spc') else ''

            if (product_name, type) in seen:
                continue

            print(active_substance + ' : number ' + str(n))
            print(product_name)
            print(link)
            print(pdf_name)
            print()

            if type == '':
                continue

            # Link to PDF expired
            try:
                xml = Parser.convert_pdf(link, format='xml')
            except Exception as e:
                continue

            should_continue = False

            while (True):
                try:
                    if type == 'leaflet':
                        # Characters in PDF with no representation in the encoding used by the XML parser, ignore
                        paras = extractParagraphsLeaflet.extract_paragraphs(xml)

                        # PDF contains no embedded text
                        if paras == []:
                            should_continue = True
                            break

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
                        paras = extractParagraphsSPC.extract_paragraphs(xml)

                        if paras == []:
                            should_continue = True
                            break

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
                    break

                except ClientError as e:
                    # We have exceeded the provisioned database throughput, sleep before putting more items
                    print('sleeping')
                    print()
                    time.sleep(1)

            if (should_continue):
                continue

            seen.append((product_name, type))

