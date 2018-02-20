import parsing.GParser as Parser
import parsing.ClearXML as ClearXML
import parsing.extractParagraphs as extractParagraphs
import boto3

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

with drugsTable.batch_writer() as batch:
    csvs = csvResponse['Items']
    for drug in linksResponse['Items']:
        active_substance = drug['drug']
        data = drug['data']
        seen = []
        csv = {}
        for csv_ in csvs:
            name = csv_['drug']
            if (name in active_substance or active_substance in name):
                csv = csv_
                break
        for product in data:
            link = product['link']
            product_name = product['product']
            pdf_name = product['pdf_name']
            type = 'leaflet' if pdf_name.startswith('leaflet') else 'spc'
            if (product,type) in seen:
                continue
            if type == 'leaflet':
                xml = Parser.convert_pdf(link, format='xml')
                clear_xml = ClearXML.clear_XML_from_text_tags(xml)
                paras = extractParagraphs.extract_paragraphs(clear_xml)
                if product_name in [t[0] for t in seen]:
                    batch.update_item(
                        Key={
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
                        batch.put_item(
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
                        batch.put_item(
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
            #else:
            seen.append((product_name, type))

