from datetime import datetime
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi.responses import StreamingResponse

def connect_to_s3_resource():
    s3 = boto3.resource(
        's3',
        aws_access_key_id='AKIA5N6KSCCMOEUZ4IWX',
        aws_secret_access_key='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',
        region_name='eu-west-2',
    )
    return s3

def upload_doc(filename, name='Meeting_test.docx'):
    s3 = connect_to_s3_resource()
    try:
        bucket = 'sribucket000'
        
        s3.Object(bucket, name).put(Body=filename)
        print(f"File '{name}' uploaded to bucket '{bucket}'.")
    except (BotoCoreError, ClientError) as e:
        print(f"Error uploading file: {e}")