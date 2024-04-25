FROM python:3.12.1

ADD c1.py .

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./c1.py"]