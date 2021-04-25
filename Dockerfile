FROM python:3.6-alpine

RUN adduser -D daybalance

WORKDIR /home/daybalance

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY daybalance.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP daybalance.py

RUN chown -R daybalance:daybalance ./
USER daybalance

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
