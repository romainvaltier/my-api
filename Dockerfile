FROM python:3.11-slim as build

WORKDIR /usr/app
RUN python -m venv /usr/app/venv
ENV PATH="/usr/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --quiet --no-cache-dir --use-pep517 -r requirements.txt

FROM python:3.11-slim
LABEL org.opencontainers.image.authors="romain@valtier.fr"

RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python

RUN mkdir /usr/app && chown python:python /usr/app
WORKDIR /usr/app

COPY --chown=python:python --from=build /usr/app/venv ./venv
COPY --chown=python:python ./app .

USER 999

EXPOSE 8000

ENV PATH="/usr/app/venv/bin:$PATH"
CMD [ "uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000" ]
