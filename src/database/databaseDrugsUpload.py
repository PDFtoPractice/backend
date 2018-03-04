import time

import boto3
from botocore.exceptions import ClientError

import paragraph_extraction.extraction.extractParagraphsLeaflet as extractParagraphsLeaflet
import paragraph_extraction.extraction.extractParagraphsSPC as extractParagraphsSPC
import paragraph_extraction.parsing.GParser as Parser

# Get database resource
dynamodb = boto3.resource('dynamodb')

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

# Get handle on the sources in the database
csvTable = dynamodb.Table('csv_advice')
linksTable = dynamodb.Table('leaflet_links')
drugsTable = dynamodb.Table('drugs')

# Scan the csv table and fetch the items
csvResponse = csvTable.scan()
csvs = csvResponse['Items']

# Scan the links table
linksResponse = linksTable.scan()
not_first_iter = False

# While there are more links to fetch from the table, scan the table
while 'LastEvaluatedKey' in linksResponse:

    # Do not scan if on the first iteration as we have already scanned
    if (not_first_iter):
        linksResponse = linksTable.scan(
            ExclusiveStartKey=linksResponse['LastEvaluatedKey']
        )

    # For each item in the links response get the active substance and data maps
    for drug in linksResponse['Items']:
        active_substance = drug['drug']

        data = drug['data']
        seen = []
        csv = {}

        # See if there is any information in the csv about the active substance
        for csv_ in csvs:
            name = csv_['drug']
            if (name.lower() in active_substance.lower() or active_substance.lower() in name.lower()):
                csv = csv_
                break

        # For each product under the active substance fetch a leaflet and summary of product characteristics
        # and extract the pdfs into paragraphs to be inserted into the database
        for product in data:
            link = product['link']
            product_name = product['product']
            pdf_name = product['pdf_name']
            type = 'leaflet' if pdf_name.startswith('leaflet') else 'spc' if pdf_name.startswith('spc') else ''

            # We have already collected a leaflet of this type for the given product
            if (product_name, type) in seen:
                continue

            print(active_substance)
            print(product_name)
            print(link)
            print(pdf_name)
            print()

            # The pdf is neither a leaflet or a summary of product characteristics - ignore the pdf
            if type == '':
                continue

            # Internal failure in the pdfminer.six library - the pdf cannot be parsed, or the url has expired - ignore the pdf
            try:
                xml = Parser.convert_pdf(link, format='xml')
            except Exception as e:
                continue

            while (True):
                try:
                    if type == 'leaflet':
                        paras = extractParagraphsLeaflet.extract_paragraphs(xml)

                        # PDF contains no embedded text - ignore it
                        if paras == []:
                            should_continue = True
                            break

                        # Create item if not already in database, and add paragraphs
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

                        # PDF contains no embedded text - ignore it
                        if paras == []:
                            should_continue = True
                            break

                        # Create item if not already in database, and add paragraphs
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
                    # We have exceeded the provisioned database throughput, sleep before putting more items to reduce the write rate
                    print('sleeping')
                    print()
                    time.sleep(1)

            # We no longer want to process pdfs of this type associated with the product
            seen.append((product_name, type))

    not_first_iter = True
