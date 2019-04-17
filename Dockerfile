FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ENTRYPOINT ["ablog"]
