FROM ubuntu:14.04
MAINTAINER Joakim Norrgard "joakim.norrgard@ericsson.com"
ENV REFRESHED_AT 2015-02-15
RUN apt-get update -yqq
RUN apt-get -yqq install default-jre-headless
RUN apt-get -yqq install apache2
RUN apt-get -yqq install praat
RUN apt-get -yqq install libapache2-mod-php5

ADD ias.tar.gz /var/www/html

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2

RUN mkdir -p $APACHE_RUN_DIR $APACHE_LOG_DIR $APACHE_LOCK_DIR
RUN chown -R www-data:www-data /var/www

EXPOSE 80
ENTRYPOINT ["/usr/sbin/apache2"]
CMD ["-D", "FOREGROUND"]
