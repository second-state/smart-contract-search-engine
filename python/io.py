
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

cors = CORS(app, resources={r"/py/*": {"origins": "localhost"}})

@app.route("/py/sg")
def output():
    results = es.get(index='fairplay', id='0x9719bee8b984adde1bfd6ae432e79e323909dc2ea81fdeab02e019200b3fc3a5')
    return jsonify(results['_source'])

#@app.route("/output")
#def output():
#  return "Hello World!"

if __name__ == "__main__":
  app.run(debug=True)