FROM python:3.12.12-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY . /app
CMD ["bash","-c","flask --app lab2_app run --host=0.0.0.0 --port=$PORT"]
