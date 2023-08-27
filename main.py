from typing import Annotated
import pandas as pd
import chardet
from io import BytesIO

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')

@app.post("/")
async def do_callings(excel_csv_file : Annotated[UploadFile, File(description='Csv file with contacts')], audio_file: Annotated[UploadFile, File(description='Audio file that has to be played during a phone call')]):
    allowed_excel_extensions = ['xlsx', 'csv']
    allowed_audio_extensions = ['mp3', 'wav']

    excel_extension = excel_csv_file.filename.split(".")[-1]
    audio_extension = audio_file.filename.split(".")[-1]

    if excel_extension not in allowed_excel_extensions or audio_extension not in allowed_audio_extensions:
        return JSONResponse(content="Invalid file extension. Allowed extensions: xlsx, csv for Excel/CSV, mp3, wav for audio.", status_code=400)

    excel_csv_content = await excel_csv_file.read()

    try:
        detected_encoding = chardet.detect(excel_csv_content)["encoding"]
        excel_csv_df = pd.read_csv(BytesIO(excel_csv_content), encoding=detected_encoding)
        print(excel_csv_df)
        # You can now work with excel_csv_df as a Pandas DataFrame
    except pd.errors.ParserError as e:
        return JSONResponse(content=f"Error reading CSV: {str(e)}", status_code=400)

    return JSONResponse(content="Files uploaded and read successfully.")


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})