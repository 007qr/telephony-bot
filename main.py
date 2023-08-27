from typing import Annotated
import pandas as pd
import chardet
from io import BytesIO
import time
import boto3 
import os
from dotenv import load_dotenv
from twilio.rest import Client

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Load environment variables from .env file
load_dotenv()

# Access TWILIO environment variables
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
mobile_number = os.environ['MOBILE_NUMBER']

# Access AWS environment variables
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
s3_region_name = os.environ.get("S3_REGION_NAME")

# client = Client(account_sid, auth_token)
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Amazon S3 Configuration
S3_BUCKET_NAME = s3_bucket_name
S3_REGION_NAME = s3_region_name
s3_client = boto3.client(
    "s3",
    region_name=S3_REGION_NAME,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)


def upload_to_s3(file, filename):
    s3_client.upload_fileobj(file, S3_BUCKET_NAME, filename)


@app.post("/")
async def do_callings(
    excel_csv_file: Annotated[UploadFile, File(description="Csv file with contacts")],
    audio_file: Annotated[
        UploadFile,
        File(description="Audio file that has to be played during a phone call"),
    ],
):
    allowed_excel_extensions = ["xlsx", "csv"]
    allowed_audio_extensions = ["mp3", "wav"]

    excel_extension = excel_csv_file.filename.split(".")[-1]
    audio_extension = audio_file.filename.split(".")[-1]

    if (
        excel_extension not in allowed_excel_extensions
        or audio_extension not in allowed_audio_extensions
    ):
        return JSONResponse(
            content="Invalid file extension. Allowed extensions: xlsx, csv for Excel/CSV, mp3, wav for audio.",
            status_code=400,
        )

    excel_csv_content = await excel_csv_file.read()

    try:
        detected_encoding = chardet.detect(excel_csv_content)["encoding"]
        excel_csv_df = ""

        if excel_extension == "xlsx":
            excel_csv_df = pd.read_excel(BytesIO(excel_csv_content))
        else:
            excel_csv_df = pd.read_csv(
                BytesIO(excel_csv_content), encoding=detected_encoding
            )

        try:
            for number in excel_csv_df["Phone_numbers"]:
                call = client.calls.create(
                        method='GET',
                        url='http://demo.twilio.com/docs/voice.xml',
                        to=f'{number}',
                        from_=f'{mobile_number}'
                    )
                print(call.sid)
        except KeyError:
            return JSONResponse(content=f"Error reading CSV", status_code=400)

    except pd.errors.ParserError as e:
        return JSONResponse(content=f"Error reading CSV: {str(e)}", status_code=400)

    # Upload audio file to Amazon S3
    audio_extension = audio_file.filename.split(".")[-1]
    audio_file_content = await audio_file.read()
    s3_audio_filename = f"{time.time()}_audio_{audio_file.filename}"
    try:

        upload_to_s3(BytesIO(audio_file_content), s3_audio_filename)

    except Exception as e:
        return JSONResponse(content="Error uploading audio file", status_code=400)

    # Send Calls
    # f"https://telephony-bot.s3.ap-south-1.amazonaws.com/{s3_audio_filename}"

    return JSONResponse(
        content="Files uploaded and read successfully.", status_code=200
    )


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})
