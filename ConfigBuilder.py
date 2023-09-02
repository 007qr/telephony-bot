from dotenv import load_dotenv
import boto3
from twilio.rest import Client
from twilio.rest.insights.v1.call import CallInstance


import os


class ConfigBuilder:
    def __init__(self):
            # Load environment variables from .env file
        load_dotenv()

        self.header_name = "Phone_numbers"

        # Access TWILIO environment variables
        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']
        self.auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.mobile_number = os.environ['MOBILE_NUMBER']
        
        # Access AWS environment variables
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
        self.s3_region_name = os.environ.get("S3_REGION_NAME")

    def get_boto3_client(self):
        s3_client = boto3.client("s3", region_name=self.s3_region_name, 
        aws_access_key_id=self.aws_access_key_id, 
        aws_secret_access_key=self.aws_secret_access_key)
        return s3_client
    
    def upload_to_s3(self, s3_client, file_content, filename):
        s3_client.upload_fileobj(file_content, self.s3_bucket_name, filename, ExtraArgs={'ContentType': "audio/mpeg"} )

    def get_twilio_client(self):
        return Client(self.account_sid, self.auth_token)

    def twilio_call(self, client, url, mobile_number) -> CallInstance:
        call = client.calls.create(
            method='GET', 
            url=url, 
            to=f'{mobile_number}', 
            from_=f'{self.mobile_number}' )
        return call
    
    def twilio_message(self, client, txt, mobile_number) -> None:
        message = client.messages.create(from_=f'{self.mobile_number}', to=f'{mobile_number}', body=txt)
        print(message.sid)
    


