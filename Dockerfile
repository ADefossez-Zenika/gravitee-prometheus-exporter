FROM python:3

COPY app /app

RUN pip install -r requirements.txt 

ENTRYPOINT ["python", "/app/application.py"]