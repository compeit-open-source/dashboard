FROM ubuntu:14.04
MAINTAINER Joakim Norrgard "joakim.norrgard@ericsson.com"
ENV REFRESHED_AT 2015-02-11
RUN apt-get update -yqq
RUN apt-get install -yqq python2.7
RUN apt-get install -yqq python2.7-dev
RUN apt-get install -yqq python-pip

COPY requirements.txt /root/
RUN pip install -r /root/requirements.txt

ADD dashboard.tar.gz /root
RUN /root/manage.py sample_db

EXPOSE 8000

CMD [ "/root/manage.py", "server"]