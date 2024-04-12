FROM python:3.8.3-slim
LABEL maintainer="irvan9110@gmail.com"
COPY . ./usr/src/app
WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN pip install -r requirements.txt 

EXPOSE 5000

ENTRYPOINT ["python"]
CMD [ "run.py" ]

# CMD ["flask","run","--debug"]