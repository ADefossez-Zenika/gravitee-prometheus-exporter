FROM python:3

COPY app /app

RUN pip install -r /app/requirements.txt 

ENTRYPOINT ["python", "/app/application.py"]