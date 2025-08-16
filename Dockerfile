FROM python:3.13.7-alpine

WORKDIR /app
COPY src src
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]
