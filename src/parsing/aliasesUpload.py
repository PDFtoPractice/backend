from __future__ import print_function # Python 2/3 compatibility
import boto3
import entityRecog as EntityRecog
import urllib

dynamodb = boto3.resource('dynamodb')
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')



aliases_table = dynamodb.Table('aliases')

aliases_table.meta.client.get_waiter('table_exists').wait(TableName='aliases')
linksTable = dynamodb.Table('leaflet_links')
linksResponse = linksTable.scan()
log = 0
for drug in linksResponse['Items']:
    data = drug['data']
    for product in data:
        link = product['link']
        pdf_name = product['pdf_name']
        product_name = product['product']
        if pdf_name.startswith('leaflet MAH GENERIC_PL'):
            names = []
            group_of_meds = []
            purpose = []
            aliases = []
            try:
                names, group_of_meds, purpose = EntityRecog.get_aliases(link)
                print(names, group_of_meds, purpose)
            except urllib.error.HTTPError as e:
                print("urllib error")
                continue
            except:
                print("Error")
                continue
            if names != []:
                names = [product_name] + names
                aliases = group_of_meds
                aliases += purpose
                if aliases != []:
                    list_aliases = aliases
                    list_aliases += names
                    # items = [{'drug_name': name, aliases: } for name in names]
                    for name in names:
                        list_aliases = [alias for alias in aliases]
                        list_aliases += [alias for alias in names if alias != name]

                        print(log)
                        aliases_table.put_item(
                            Item={
                                'drug_name': name,
                                'aliases': list_aliases
                            }
                        )
                        log += 1
            else:
                if aliases != []:
                    aliases_table.put_item(
                        Item={
                            'drug_name': product_name,
                            'aliases': aliases
                        }
                    )


# def active_subst():
#     prod_active_table = dynamodb.Table('product-active')
#     linksTable = dynamodb.Table('leaflet_links')
#     linksResponse = linksTable.scan()
#     for drug in linksResponse['Items']:
#         data = drug['data']
#         for product in data:
#             link = product['link']
#             pdf_name = product['pdf_name']
#             product_name = product['product']
#




