FROM python:3.9

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY database_controller.py main.py /

CMD ["python", "/main.py"]

