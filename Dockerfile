FROM python:3.11-slim-bookworm

# Avoid warnings by switching to noninteractive
ARG DEBIAN_FRONTEND=noninteractive

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

ENV PYTHONUNBUFFERED 1
ENV EODAG__HYDROWEB_NEXT__AUTH__CREDENTIALS__APIKEY fakeapikey
#ENV HYDROWEBNEXT_SCRIPTS_HYDROWEB_PRODUCT_NAMES HYDROWEB_RIVERS_OPE,HYDROWEB_LAKES_OPE,HYDROWEB_RIVERS_RESEARCH,HYDROWEB_LAKES_RESEARCH
#ENV HYDROWEBNEXT_SCRIPTS_BASIN NIGER
#ENV HYDROWEBNEXT_SCRIPTS_BBOX_WKT POLYGON ((-10.3800 5.2930, 14.0680 5.2930, 14.0680 17.1080, -10.3800 17.1080, -10.3800 5.2930))
#ENV HYDROWEBNEXT_SCRIPTS_DEST_FOLDER /tmp/niger_basin


RUN apt-get update \
    && apt-get -y install python3-venv \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Use a virtualenv
RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# installs common to builder & production
COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/

CMD ["python3", "cli.py", "download-on-watershed"]