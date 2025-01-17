from fastapi import FastAPI, UploadFile, File,HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import redis
from typing import Optional, Dict,List
from src.ml.codeanalyzer import CodeAnalyzer
import os


app = FastAPI(title="CodeReviewer")
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


#if post file_name is called then this gets function executes
@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    #if the file is not a python file then raise this exception
    if not file.filename.endswith('.py'):
        raise HTTPException(
            status_code=400,
            details=" Only PY files allowed"
        )
    try:
        #Read the contents of the file pause the function and wait for this to complete
        content = await file.read()
        #translate binary file into UTF-8
        code = content.decode('utf-8')
        #Analyze the Code
        analysisResults = codeanalyzer.analyze_code_snippet(code)
        #Add file into the analysis
        analysisResults['file info'] = {'filename':file.filename,'size': len(content)}
        #Display the info
        return JSONResponse(content= analysisResults)
    #Display Any problems that Might occur
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= f"Analysis Failed: {str(e)}"
        )
#This gets called if mutilple files post is ever called
@app.post("/analyze-multiple-files")
async def analyze_multiple_files(files: List[UploadFile] = File(...)):
# Does the same exact thing as analyze file but goes through ever single file and returns results
    results ={}
    for file in files:
        if not file.filename.endswith('.py'):
            continue
        try:
            content = await file.read()
            code = content.decode('utf-8')
            analysis = codeanalyzer.analyze_code_snippet(code)
            results[file.filename] = analysis
        #If an error ever does occur then add the error to the results file
        except Exception as e:
            results[file.filename] = {"error": str(e)}
    return results
#Check if the service is healthy
@app.get("/health")
async def health_check():
    #if codeanlayze has been initilized then return that it is healthy else unhealthy
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


