import os
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sagemaker_client = boto3.client('sagemaker-runtime')
ENDPOINT_NAME = os.environ.get('SAGEMAKER_ENDPOINT_NAME', 'smart-prediction-endpoint')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        # API Gateway proxy integration event body okuma
        body = event.get('body', '{}')
        if isinstance(body, str):
            body_data = json.loads(body)
        else:
            body_data = body
            
        logger.info(f"Forwarding payload to SageMaker: {json.dumps(body_data)}")
        
        # SageMaker Endpoint'ini tetikle
        response = sagemaker_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='application/json',
            Body=json.dumps(body_data)
        )
        
        # Sonucu oku ve decode et
        result_body = response['Body'].read().decode('utf-8')
        result_json = json.loads(result_body)
        
        logger.info(f"SageMaker response: {result_body}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps(result_json)
        }
    except Exception as e:
        logger.error(f"Error invoking SageMaker endpoint: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
