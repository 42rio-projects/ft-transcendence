FROM python

WORKDIR /usr/src/app

COPY ./tools/script.sh /

RUN pip install --upgrade pip && \
    pip install django \
                psycopg[binary] \
                djangorestframework \
                django-phonenumber-field phonenumbers \
                djangorestframework_simplejwt \
				channels[daphne] \
				channels_redis \
                twilio

# Script to wait for a host:port to be available
RUN curl -fsSLo /wait-for-it.sh \
                https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod +x /wait-for-it.sh

ENTRYPOINT ["/wait-for-it.sh", "postgres:5432", "--", "/script.sh"]
