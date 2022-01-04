FROM python:3.9
EXPOSE 5000
RUN pip install --upgrade pip
WORKDIR /flask_app
COPY requirements.txt /flask_app/
RUN pip install -r requirements.txt --no-cache-dir
