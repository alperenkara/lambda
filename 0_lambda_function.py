import base64
import datetime
import json
import logging
import os

import boto3
import requests
from requests_aws4auth import AWS4Auth


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get OpenSearch service settings from environmental variables
es_url = os.getenv("ES_URL")
region = os.getenv("REGION")

# Get credentials
credentials = boto3.Session().get_credentials()
aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es', session_token=credentials.token)

record = {"timestamp": "02/02/2002", "name": 'Veli', "confidence": 0.2}

def process_record(record):
    confidence = 0.1
    name = 'Alperen'
    timestamp = "01/01/2001"
    
    data = {"timestamp": timestamp, "name": name, "confidence": confidence}
    
    response = requests.post(f"{es_url}/face/_doc/",
        auth=aws_auth,
        headers={"Content-Type": "application/json"},
        json=record)

def lambda_handler(event, context):
    process_record(record)
    return {"result": "ok"}
