# Download the helper library from https://www.twilio.com/docs/python/install
from dotenv import load_dotenv

import os
from requests import HTTPError
from twilio.base.exceptions import TwilioRestException
from twilio.http import TwilioException
from twilio.rest import Client

load_dotenv()
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
mobile_number = os.environ['MOBILE_NUMBER']
client = Client(account_sid, auth_token)

try:
    call = client.calls.create(
                        method='GET',
                        url='https://telephony-bot.s3.ap-south-1.amazonaws.com/file_example_MP3_1MG.mp3',
                        to='+919209217376',
                        from_="+18448138736"
                    )

except TwilioRestException as e:
    print(e)
    print("Something went wrong!")
# print(call.sid)