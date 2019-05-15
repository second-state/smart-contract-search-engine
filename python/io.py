
#IMPORTS
import json
import boto3 
import requests
import elasticsearch.helpers
from flask_cors import CORS, cross_origin
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

CORS(app)

@app.route("/data1")
def data1():
    results = elasticsearch.helpers.scan(client=es, index="fairplay_v1", query=json.dumps(request), preserve_order=True)
    #es.get(index='fairplay', id='0x5bebceb6f96973a3fa4e377760637d8515c1beec17c664aa26747ccf99ad866c')
    return jsonify(results['_source'])

@app.route("/data2")
def data2():
    results = elasticsearch.helpers.scan(client=es, index="fairplay_v1", query=json.dumps(request), preserve_order=True)
    return jsonify(results['_source'])

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)
