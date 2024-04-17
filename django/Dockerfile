# FROM python

FROM python:3.9-slim-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
# COPY ./requirements/requirements.txt .

# Run the application:
COPY ./app .
COPY ./tools/script.sh /
COPY ./tools/wait-for-it.sh /
# COPY /home/dvargas/Desktop/ft_transcendence/README.md .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Script to wait for a host:port to be available
RUN chmod +x /wait-for-it.sh

ENTRYPOINT ["/wait-for-it.sh", "postgres:5432", "--", "/script.sh"]
