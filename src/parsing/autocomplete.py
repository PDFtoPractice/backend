from __future__ import print_function # Python 2/3 compatibility
import boto3

dynamodb = boto3.resource('dynamodb')
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')



aliases_table = dynamodb.Table('product-active')

aliases_table.meta.client.get_waiter('table_exists').wait(TableName='product-active')
aliasesResponse = aliases_table.scan()
f = open('sample_outputs/product-active.txt', 'w')
names = []
for item in aliasesResponse['Items']:
    active_substances = item['active']
    product_name = item['product'].lower()
    active_substances = [actvsub.lower() for actvsub in active_substances]
    product_name = product_name
    names.append([product_name, active_substances])
f.write(str(names))
f.close()









