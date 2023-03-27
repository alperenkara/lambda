import json
import urllib.parse
import boto3
import sys
import pandas as pd
import io
from elasticsearch import Elasticsearch

print('Loading function')

# Get OpenSearch service settings from environmental variables
es_url = os.getenv("ES_URL")
region = os.getenv("REGION")

# Get credentials
credentials = boto3.Session().get_credentials()
aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es', session_token=credentials.token)

#s3 = boto3.client('s3')
s3 = boto3.resource('s3')

es = Elasticsearch("your_url")
index = "github_commit"
body = {
        "mappings": {
            "properties": {
                "CommitID": {
                    "type": "text"
                },
                "Name":{
                    "type": "text"
                },
                "Date": {
                    "type": "text"
                },
                "Address": {
                    "type": "text"
                }
            # }
            }
        },
        "settings": {
            "index" : {
                "number_of_shards" : 1,
                "number_of_replicas" : 0
            }
        }
        
}

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
    
        obj = s3.Object(bucket, key)
        s3data = obj.get()['Body'].read() #.decode('utf-8')
        csv = pd.read_excel(io.BytesIO(s3data))
        parsed_csv = csv.to_dict()
        print(parsed_csv)
        bulk_api_body = []
        print(len(parsed_csv['CommitID']))
        for i in range(0, len(parsed_csv['CommitID'])):
            action = {"index": {"_index": index, "_id": parsed_csv['CommitID'][i]}}
            eachcommit = {
                'CommitID': parsed_csv['CommitID'][i],
                ' Name': parsed_csv['Name'][i],
                'Date': parsed_csv['Date'][i],
                'Address': parsed_csv['Address'][i]
            }
            bulk_api_body.append(action)
            bulk_api_body.append(eachcommit)
        print(bulk_api_body)
        response = addData(bulk_api_body)
        if not response:
            print("could not add data to ES")
            return "could not add data to ES"
        
        return "Pushed to ES"
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e


def es_reachable():
    return es.ping()
    
def index_exist():
    return es.indices.exists(index=index)

def addData(bulk_api_body):
    if not es_reachable:
        print("ES not reachable")
        return false
    if not index_exist():
        print("Index Doesnot exist. Creating index")
        response = es.indices.create(index=index, body=body)  
        # settings=index_settings, mappings=index_mapping)
        if not response['acknowledged']:
            print("Failed to create index")
            return false
    print("adding data to ES")
    es.bulk(index=index, body=bulk_api_body)
    return True
