import decimal
import boto3
import json
import os

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def has_allowed_params(params):
    allowed_params = {'limit', 'provider'}
    if params:
        return allowed_params >= params.keys()
    else:
        return True

def api_response(status, body):
    payload = {
        "isBase64Encoded": True,
        "statusCode": status,
        "headers": {'Content-Type': 'application/json'},
        "body": json.dumps(body, default=decimal_default)
    }
    return payload

def get_limit(params):
    try:
        limit = int(params['limit'][0])
        params.pop('limit', None)
    except (ValueError, TypeError):
        limit = int(os.environ['ARTICLE_LIMIT'])
    return limit

def article_handler(method, params):
    dynamodb = boto3.resource('dynamodb')
    article_table = dynamodb.Table(os.environ['ARTICLE_DYNAMODB_TABLE'])
    limit = get_limit(params)
    if not params:
        return article_table.scan(Limit=limit)['Items']
    
def topic_handler(method, params):
    dynamodb = boto3.resource('dynamodb')
    topic_table = dynamodb.Table(os.environ['TOPIC_DYNAMODB_TABLE'])
    limit = get_limit(params)
    if not params:
        return article_table.scan(Limit=limit)['Items']

def lambda_handler(event, context):

    print(event)

    resource_functions = {
        "articles": article_handler,
        "topcics": topic_handler
    }

    resource_path = event['resource'].split("/")
    resource = resource_path[-1]
    query_parameters = event['multiValueQueryStringParameters']
    http_method = event['httpMethod']

    if not(has_allowed_params(query_parameters)):
        return api_response(400, {"Message": "Incorrect query string specified"})
    
    try:
        body = resource_functions[resource](http_method, query_parameters)
    except Exception as e:
        return api_response(500, {"Message": "There was a problem handling this request"})

    print(api_response(200, body))

    return api_response(200, body)