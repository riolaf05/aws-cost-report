import json
import os
import logging
import requests
from datetime import date
import boto3

# Initializing a logger and settign it to INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Reading environment variables and generating a Telegram Bot API URL
TOKEN = os.environ['TOKEN']
USER_ID = os.environ['USER_ID']
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage".format(TOKEN)

# Helper function to prettify the message if it's in JSON
def process_message(input):
    try:
        # Loading JSON into a string
        raw_json = json.loads(input)
        # Outputing as JSON with indents
        output = json.dumps(raw_json, indent=4)
    except:
        output = input
    return output

def get_data():
    # Accessing Cost Explorer API
    client = boto3.client('ce')
    
    # StartDate = 1st date of current month, EndDate = Todays date
    start_date=str(date(year=date.today().year, month=date.today().month, day=1).strftime('%Y-%m-%d'))
    end_date=str(date.today())
    
    print(f'StartDate:{start_date} - EndDate:{end_date}\n')
    
    # The get_cost_and_usage operation is a part of the AWS Cost Explorer API, which allows you to programmatically retrieve cost and usage data for your AWS accounts.
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start':start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        Filter={
            "Not":
            {
                'Dimensions':{
                'Key': 'RECORD_TYPE',
                'Values':['Credit','Refund']
                 }
            }
        },
        GroupBy=[
            {
                'Type':'DIMENSION',
                'Key':'SERVICE'
            }
        ]
    )
    
    mydict=response
    resource_name=[]
    resource_cost=[]
    
    total_resources_active = len(mydict['ResultsByTime'][0]['Groups'])
    
    for i in range (total_resources_active):
        a=(mydict['ResultsByTime'][0]['Groups'][i].values())
        b=list(a)
        resource_name.append(b[0][0])
        resource_cost.append(float(b[1]['UnblendedCost']['Amount']))
    
    dict0={}
    
    for i in range(total_resources_active):
        dict0[resource_name[i]]=resource_cost[i]
    
    billed_resources={k: v for k, v in dict0.items() if v}

    #total cost
    total = sum(billed_resources.values())

    print(f'Total Billed Amount:-', total)
    print(f'Current Billed Resources of this month:-',json.dumps(billed_resources, indent=4, sort_keys=True))
    print(f'Active Resources:-', json.dumps(resource_name, indent=4, sort_keys=True))
    #print(billed_resources,resource_name)
    return billed_resources, resource_name, total

# Main Lambda handler
def lambda_handler(event, context):
    # logging the event for debugging
    logger.info("event=")
    logger.info(json.dumps(event))

    # Basic exception handling. If anything goes wrong, logging the exception    
    try:
        
        bill,resource,total=get_data()
        message = 'Report costi subscription AWS\n\nTotal Billed Amount:- {}\n\nCurrent Billed Resources of this month:- {}\n\nActive Resources:- {}\n'.format(total, json.dumps(bill, indent=4, sort_keys=True),  json.dumps(resource, indent=4, sort_keys=True))

        # Payload to be set via POST method to Telegram Bot API
        payload = {
            "text": message.encode("utf8"),
            "chat_id": USER_ID
        }

        # Posting the payload to Telegram Bot API
        requests.post(TELEGRAM_URL, payload)

    except Exception as e:
        raise e