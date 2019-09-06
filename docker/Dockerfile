FROM ubuntu:18.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        apache2 \
        cron \
        awscli \
        curl \
        python3 \
        python3-pip \
        supervisor \
        vim && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install \
    Flask \
    aws_requests_auth \
    boto3 \
    elasticsearch \
    requests \
    web3

COPY config/site.conf /etc/apache2/sites-available/search-engine.conf
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY *.html /var/www/html/
COPY css/ /var/www/html/css/
COPY images/ /var/www/html/images/
COPY js/ /var/www/html/js/
COPY python/ /app

RUN a2dissite 000-default.conf && \
    a2ensite search-engine.conf && \
    a2enmod proxy && \
    a2enmod rewrite && \
    a2enmod headers && \
    a2enmod proxy_http

WORKDIR /app
EXPOSE 80 443
CMD supervisord
