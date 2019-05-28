
#IMPORTS
import os
import json
import boto3 
import requests
import configparser
import elasticsearch.helpers
from flask import Flask, jsonify, request
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection 

# CONFIG

# CWD
scriptExecutionLocation = os.getcwd()
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(os.path.join(scriptExecutionLocation, 'config.ini'))

host = config['elasticSearch']['endpoint']
print("ElasticSearch Endpoint: %s" % host)

elasticSearchAwsRegion = config['elasticSearch']['aws_region']

auth = BotoAWSRequestsAuth(aws_host=host, aws_region=elasticSearchAwsRegion, aws_service='es')
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    region=elasticSearchAwsRegion,
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

app = Flask(__name__)

@app.route("/api/data1", methods=['GET', 'POST'])
def data1():
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=es, index="fairplay", query=jsonRequestData)
    print(results)
    obj = {}
    num = 1
    for item in results:
        obj[str(num)] = item
    print(obj)
    return jsonify(obj)

@app.route("/api/data2", methods=['GET', 'POST'])
def data2():
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=es, index="fairplay", query=jsonRequestData)
    print(results)
    obj = {}
    num = 1
    for item in results:
        obj[str(num)] = item
    print(obj)
    return jsonify(obj)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8080, debug=True)
