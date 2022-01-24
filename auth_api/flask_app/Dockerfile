FROM python:3.9
EXPOSE 5000
RUN pip install --upgrade pip
WORKDIR /auth_api/flask_app
COPY requirements.txt /auth_api/flask_app/
RUN pip install -r requirements.txt --no-cache-dir
#ENTRYPOINT ["uwsgi", "--socket", "0.0.0.0:5000", "--protocol=http", "-w", "wsgi:app"]
ENTRYPOINT ["python", "app.py"]