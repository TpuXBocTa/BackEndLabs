FROM python:3.12.12-slim-bookworm
WORKDIR /my_app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY . /my_app
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]