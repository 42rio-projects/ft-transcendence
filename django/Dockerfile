FROM python:3.9-slim-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


COPY ./app .
COPY ./tools/script.sh /
COPY ./tools/wait-for-it.sh /

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN chmod +x /wait-for-it.sh

ENTRYPOINT ["/wait-for-it.sh", "postgres:5432", "--", "/script.sh"]
