import decimal
import boto3
import json
import os

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

class CoffeePotApi:

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

    def _has_allowed_params(self, params):
        allowed_params = {'limit', 'provider'}
        if params:
            return allowed_params >= params.keys()
        else:
            return True

    def _api_response(self, status, body):
        payload = {
            "isBase64Encoded": True,
            "statusCode": status,
            "headers": {'Content-Type': 'application/json'},
            "body": json.dumps(body, default=decimal_default)
        }
        return payload

    def _get_limit(self, params):
        try:
            limit = int(params['limit'][0])
            params.pop('limit', None)
        except (ValueError, TypeError):
            limit = int(os.environ['ARTICLE_LIMIT'])
        return limit

    def _article_handler(self, method, params):
        article_table = self.dynamodb.Table(os.environ['ARTICLE_DYNAMODB_TABLE'])
        limit = self._get_limit(params)
        if not params:
            return article_table.scan(Limit=limit)['Items']

    def _topic_handler(self, method, params):
        topic_table = self.dynamodb.Table(os.environ['TOPIC_DYNAMODB_TABLE'])
        limit = self._get_limit(params)
        if not params:
            return topic_table.scan(Limit=limit)['Items']
    
    def execute(self, event):

        resource_functions = {
            "articles": self._article_handler,
            "topics": self._topic_handler
        }

        resource_path = event['resource'].split("/")
        resource = resource_path[-1]
        query_parameters = event['multiValueQueryStringParameters']
        http_method = event['httpMethod']
    
        if not(self._has_allowed_params(query_parameters)):
            return self._api_response(400, {"Message": "Incorrect query string specified"})

        try:
            body = resource_functions[resource](http_method, query_parameters)
        except Exception as e:
            return self._api_response(500, {"Message": "There was a problem handling this request"})

        return self._api_response(200, body)

def lambda_handler(event, context):
    return CoffeePotApi().execute(event)

if __name__ == "__main__":
    print(lambda_handler(
        {
            "resource": "/topics",
            "multiValueQueryStringParameters": "",
            "httpMethod": "POST"
        },
        None
    ))