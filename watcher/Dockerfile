FROM python:3.9

COPY requirements.txt database_controller.py main.py reload_kamailio.py /

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "/main.py"]