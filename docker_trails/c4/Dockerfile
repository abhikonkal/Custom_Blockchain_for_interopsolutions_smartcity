FROM python:3.12.1

ADD c4.py .

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./c4.py"]