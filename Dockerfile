#Install this version of python 
FROM python:3.11-slim
#Sets the working directory
WORKDIR /app
#Copeis the requirment txt and then install whats listed in it
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
#Specifices the command that will run when the container starts
CMD ["uvicorn", "src.api.endpoints:app", "--host", "0.0.0.0", "--port", "8000"]