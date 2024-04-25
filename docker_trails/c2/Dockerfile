FROM python:3.12.1

ADD c2.py .

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./c2.py"]