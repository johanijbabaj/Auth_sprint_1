FROM python:3.10
EXPOSE 8000
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir
COPY . /code/
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]