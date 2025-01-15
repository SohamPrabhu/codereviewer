from fastapi import FastAPI, UploadFile, File,HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import redis
from typing import Optional, Dict,List
from src.ml.codeanalyzer import CodeAnalyzer
import os
app = FastAPI(title="CodeReviewer")

try:
    redis_client = redis.Redis(
        host = os.getenv('REDIS_HOST', 'localhost'),
        port = int(os.getenv('REDIS_PORT',6379)),
        decode_responses= True
    )


except Exception as e:
    print(f"Couldn't Connect to a Service: {str(e)}")
codeanalyzer = CodeAnalyzer()



@app.get("/", response_class=HTMLResponse)
async def upload_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Reviewer</title>
    </head>
    <body>
        <h1>Upload Python Files for Analysis</h1>
        
        <h2>Upload a Single File</h2>
        <form action="/analyze-file" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".py" required>
            <button type="submit">Analyze File</button>
        </form>
        
        <h2>Upload Multiple Files</h2>
        <form action="/analyze-multiple-files" method="post" enctype="multipart/form-data">
            <input type="file" name="files" accept=".py" multiple required>
            <button type="submit">Analyze Files</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)



@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.py'):
        raise HTTPException(
            status_code=400,

            details=" Only PY files allowed"
        )

    try:
        content = await file.read()
        code = content.decode('utf-8')

        analysisResults = codeanalyzer.analyze_code_snippet(code)

        analysisResults['file_info'] = {'filename':file.filename,'size': len(content)}
        return JSONResponse(content= analysisResults)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= f"Analysis Failed: {str(e)}"
        )
    
@app.post("/analyze-multiple-files")
async def analyze_multiple_files(files: List[UploadFile] = File(...)):


    results ={}
    for file in files:
        if not file.filename.endswith('.py'):
            continue
        try:
            content = await file.read()
            code = content.decode('utf-8')
            analysis = codeanalyzer.analyze_code_snippet(code)
            results[file.filename] = analysis
        except Exception as e:
            results[file.filename] = {"error": str(e)}
    return results

@app.post("/analyze-code")
async def analyze_code_snippet(code:str):
    try:
        analysis = codeanalyzer.analyze_code_snippet(code)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Analysis failed:{str(e)}"
        )



@app.get("/health")
async def health_check():
    """
    Check if the service is healthy
    """
    try:
        analyzer_status = "healthy" if codeanalyzer is not None else "unhealthy"
        return {
            "status": "healthy",
            "dependencies": {
                "code_analyzer": analyzer_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


