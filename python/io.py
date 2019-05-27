
#IMPORTS
import json
import boto3 
import requests
import elasticsearch.helpers
from flask import Flask, jsonify, request
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection 

# CONFIG
host = 'search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com'
auth = BotoAWSRequestsAuth(aws_host='search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com', aws_region='ap-southeast-2', aws_service='es')
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    region='ap-southeast-2',
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

app = Flask(__name__)

@app.route("/api/data1", methods=['GET', 'POST'])
def data1():
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=es, index="fairplay", query=jsonRequestData, preserve_order=True)
    obj = {}
    num = 1
    for item in results:
        obj[str(num)] = item
    print(obj)
    return jsonify(obj)

@app.route("/api/data2", methods=['GET', 'POST'])
def data2():
    jsonRequestData = json.loads(request.data)
    results = elasticsearch.helpers.scan(client=es, index="fairplay", query=jsonRequestData, preserve_order=True)
    obj = {}
    num = 1
    for item in results:
        obj[str(num)] = item
    print(obj)
    return jsonify(obj)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8080, debug=True)
