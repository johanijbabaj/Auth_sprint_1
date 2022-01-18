FROM python:3.9
RUN pip install --upgrade pip
WORKDIR /tests
COPY requirements.txt /tests/
RUN pip install -r requirements.txt --no-cache-dir
COPY src /tests/src
COPY utils /tests/utils
COPY conftest.py /tests