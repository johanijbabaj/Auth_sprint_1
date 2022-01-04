FROM python:3.9
RUN pip install --upgrade pip
WORKDIR /tests
COPY requirements.txt /tests/
RUN pip install -r requirements.txt --no-cache-dir
COPY utils /tests/utils
COPY testdata /tests/testdata
COPY src /tests/src
COPY settings.py /tests/
COPY conftest.py /tests/
