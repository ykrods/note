FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -U pip setuptools wheel

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ENTRYPOINT ["ablog"]
