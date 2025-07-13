FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/requirements.txt

RUN python -m venv /opt/venv \
  && /opt/venv/bin/pip install -U pip setuptools wheel \
  && /opt/venv/bin/pip install -r /tmp/requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["ablog"]
