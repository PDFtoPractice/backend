from __future__ import print_function # Python 2/3 compatibility
import boto3
import csv

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

table = dynamodb.Table('perioperative_csv')


with open('..\sources\drug_instructions.csv', newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',')
    for row in csvreader:
        active_substance = row['Drug']
        advice = row['Advice']
        print("Inserting: {Drug: " + active_substance,
              "Advice: " + advice + "}")

        table.put_item(
            Item={
                'Active substance': active_substance,
                'Advice': advice,
             }
         )
