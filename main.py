from typing import Annotated
import pandas as pd
import chardet
from io import BytesIO
import time

from twilio.base.exceptions import TwilioRestException

from ConfigBuilder import ConfigBuilder

from mangum import Mangum

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

handler = Mangum(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

builder = ConfigBuilder()

boto3_client = builder.get_boto3_client()

twilio_client = builder.get_twilio_client()

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

        # Upload audio file to Amazon S3
        audio_extension = audio_file.filename.split(".")[-1]
        audio_file_content = await audio_file.read()
        s3_audio_filename = f"{time.time()}_audio_{audio_file.filename}"
        builder.upload_to_s3(boto3_client, BytesIO(audio_file_content), s3_audio_filename)

        url = f"https://telephony-bot.s3.ap-south-1.amazonaws.com/{s3_audio_filename}"

        for number in excel_csv_df[builder.header_name]:
            if len(str(number)) == 10:
                builder.twilio_call(twilio_client, url, f"+91{number}")
            else:
                builder.twilio_call(twilio_client, url, f"+{number}")
            
    except KeyError:
        return JSONResponse(content=f"Error reading CSV", status_code=400)

    except pd.errors.ParserError as e:
        return JSONResponse(content=f"Error reading CSV: {str(e)}", status_code=400)

    except TwilioRestException:
        return JSONResponse(content='Check the mobile number!', status_code=400)

    except Exception as e:
        print(e)
        return JSONResponse(content="Something went wrong!", status_code=400)

    return JSONResponse(
        content="Calls sent successfully", status_code=200
    )


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})
