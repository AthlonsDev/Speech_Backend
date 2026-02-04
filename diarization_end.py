import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


endpoint_name = 'Endpoint-20251125-131122'  # diarization endpoint

def connect_to_sm_client():
    try:
        client = boto3.client(
            'sagemaker-runtime',  # Changed from 'runtime.sagemaker'
            aws_access_key_id='AKIA5N6KSCCMOEUZ4IWX',
            aws_secret_access_key='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',
            region_name='eu-north-1',
        )
        return client
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials error: {e}")
        raise

def get_inference_component_name():
    """Get the inference component name from the endpoint"""
    try:
        sm_client = boto3.client(
            'sagemaker',
            aws_access_key_id='AKIA5N6KSCCMOEUZ4IWX',
            aws_secret_access_key='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',
            region_name='eu-north-1',
        )
        
        # List inference components for this endpoint
        response = sm_client.list_inference_components(EndpointNameEquals=endpoint_name)

        if response['InferenceComponents']:
            component_name = response['InferenceComponents'][0]['InferenceComponentName']
            print(f"Found inference component: {component_name}")
            return component_name
        else:
            print("No inference components found")
            return None
    except Exception as e:
        print(f"Error getting inference component: {e}")
        return None

def diarize(file_path):
    with open(file_path, "rb") as file:
        wav_file_read = file.read()
    
    query_endpoint(wav_file_read, "audio/wav")


def query_endpoint(body, content_type):

    print("Get creds")
    client = connect_to_sm_client()
    component_name = get_inference_component_name()
    
    # Invoke endpoint with inference component name
    try:
        if component_name:
            response = client.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType=content_type,
                Body=body,
                InferenceComponentName=component_name
            )
        else:
            response = client.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType=content_type,
                Body=body
            )
        
        print(f"Response status: {response['ResponseMetadata']['HTTPStatusCode']}")
        result = json.loads(response['Body'].read())
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error invoking endpoint: {e}")
        raise

if __name__ == "__main__":
    # diarize("backend\\temp_seg.wav")
    get_inference_component_name()
