FROM python:3.14.2-alpine

WORKDIR /app
COPY src src
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]
