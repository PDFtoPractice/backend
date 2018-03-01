import boto3
import ast

dynamodb = boto3.resource('dynamodb')
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

table = dynamodb.Table('product_active')

def cleanup():
    f = open('sample_outputs/product-active.txt', 'r')
    product_active = ast.literal_eval(f.read())
    for ls in product_active:
        # print(ls)
        product = ls[0]
        active_substances = ls[1]
        table.put_item(
            Item={
                'product': product,
                'active': active_substances
            }
        )




cleanup()